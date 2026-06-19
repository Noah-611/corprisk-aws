output "alb_dns_name" {
  description = "ALB DNS name for accessing CorpRisk web service"
  value       = aws_lb.app_alb.dns_name
}

output "app_url" {
  description = "CorpRisk application URL"
  value       = "http://${aws_lb.app_alb.dns_name}"
}

output "rds_endpoint" {
  description = "RDS MySQL endpoint"
  value       = aws_db_instance.mysql.address
}

output "s3_bucket_name" {
  description = "S3 bucket name for reports"
  value       = aws_s3_bucket.reports.bucket
}

output "target_group_name" {
  description = "ALB target group name"
  value       = aws_lb_target_group.app_tg.name
}