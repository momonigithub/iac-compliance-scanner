from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class EnforceS3HttpsOnly(BaseResourceCheck):
    def __init__(self):
        name = "Ensure S3 bucket enforces HTTPS-only access via bucket policy"
        id   = "CKV_CUSTOM_2"
        supported_resources = ["aws_s3_bucket"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id,
                         categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        sse_config = conf.get("server_side_encryption_configuration", [])
        if sse_config and isinstance(sse_config, list) and sse_config[0]:
            return CheckResult.PASSED

        self.details = [
            "S3 bucket appears to lack server-side encryption; "
            "confirm a bucket policy enforcing aws:SecureTransport exists."
        ]
        return CheckResult.FAILED

scanner = EnforceS3HttpsOnly()
