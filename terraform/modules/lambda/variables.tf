variable "function_name" {
  type = string
}

variable "source_dir" {
  type = string
}

variable "role_arn" {
  type = string
}

variable "handler" {
  type = string
}

variable "runtime" {
  type = string
  default = "python3.12"
}

variable "environment_variables" {
  type    = map(string)
  default = {}
}

