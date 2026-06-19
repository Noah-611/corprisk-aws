variable "name_prefix" {
  description = "Prefix for AWS resource names"
  type        = string
  default     = "corprisk"
}

variable "app_repo_url" {
  description = "GitHub repository URL for the CorpRisk application"
  type        = string
}

variable "opendart_api_key" {
  description = "OpenDART API key"
  type        = string
  sensitive   = true
}

variable "db_username" {
  description = "RDS MySQL username"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "RDS MySQL password"
  type        = string
  sensitive   = true
}

variable "app_port" {
  description = "FastAPI application port"
  type        = number
  default     = 8000
}