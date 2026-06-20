resource "aws_launch_template" "app" {
  name_prefix   = "${var.name_prefix}-app-"
  image_id      = data.aws_ami.amazon_linux_2023.id
  instance_type = "t3.micro"

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [aws_security_group.app_sg.id]
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    set -euxo pipefail

    exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

    dnf install -y git python3 python3-pip

    mkdir -p /opt/corprisk
    cd /opt/corprisk

    git clone --depth 1 ${var.app_repo_url} app
    cd app

    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

    cat > .env <<ENVEOF
    OPEN_DART_API_KEY=${var.opendart_api_key}
    DATABASE_URL=mysql+pymysql://${var.db_username}:${var.db_password}@${aws_db_instance.mysql.address}:3306/corprisk
    ENVEOF
    
    cat > /etc/systemd/system/corprisk.service <<SERVICEEOF
    [Unit]
    Description=CorpRisk FastAPI Application
    After=network.target

    [Service]
    User=root
    WorkingDirectory=/opt/corprisk/app
    EnvironmentFile=/opt/corprisk/app/.env
    ExecStart=/opt/corprisk/app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${var.app_port}
    Restart=always

    [Install]
    WantedBy=multi-user.target
    SERVICEEOF

    systemctl daemon-reload
    systemctl enable corprisk
    systemctl start corprisk

    sleep 10
    systemctl status corprisk --no-pager || true
    curl -f http://127.0.0.1:${var.app_port}/health || journalctl -u corprisk --no-pager -n 100
    
    # Warm up OpenDART corp code cache in background after starting the application
    cd /opt/corprisk/app
    nohup ./venv/bin/python -c "from app.dart_client import get_corp_code_list; get_corp_code_list(); print('OpenDART corp code cache warmed up')" > /var/log/corprisk-warmup.log 2>&1 &
  EOF
  )

  tag_specifications {
    resource_type = "instance"

    tags = {
      Name = "${var.name_prefix}-app"
    }
  }

  tags = {
    Name = "${var.name_prefix}-launch-template"
  }
}