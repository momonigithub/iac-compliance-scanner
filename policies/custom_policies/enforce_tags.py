from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

REQUIRED_TAGS = {"Environment", "Owner", "Project"}

TAGGED_RESOURCE_TYPES = [
    "aws_s3_bucket",
    "aws_instance",
    "aws_security_group",
    "aws_iam_role",
    "aws_db_instance",
    "aws_kms_key",
    "aws_lb",
    "aws_lb_target_group",
    "aws_autoscaling_group",
    "aws_cloudwatch_log_group",
    "aws_lambda_function",
    "aws_sns_topic",
    "aws_sqs_queue",
    "aws_vpc",
    "aws_subnet",
]

class EnforceRequiredTags(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all AWS resources have required tags: Environment, Owner, Project"
        id   = "CKV_CUSTOM_1"
        supported_resources = TAGGED_RESOURCE_TYPES
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id,
                         categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        tags = conf.get("tags", [{}])

        if isinstance(tags, list):
            tags = tags[0] if tags else {}

        if not isinstance(tags, dict):
            return CheckResult.FAILED

        present = set(tags.keys())
        missing = REQUIRED_TAGS - present

        if missing:
            self.details = [f"Missing required tags: {', '.join(sorted(missing))}"]
            return CheckResult.FAILED

        return CheckResult.PASSED

scanner = EnforceRequiredTags()
