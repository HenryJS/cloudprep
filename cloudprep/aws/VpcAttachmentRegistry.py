class VpcAttachmentRegistry:

    __registry = {}

    @staticmethod
    def register_attachment(vpc, subject, attachment):
        vpc_id = vpc.get_logical_id()
        subject_id = subject.get_logical_id()

        if vpc_id not in VpcAttachmentRegistry.__registry:
            VpcAttachmentRegistry.__registry[vpc_id] = {}

        VpcAttachmentRegistry.__registry[vpc_id][subject_id] = attachment

    @staticmethod
    def get_attachment(vpc_logical_id, subject_logical_id):
        if vpc_logical_id not in VpcAttachmentRegistry.__registry:
            return None

        if subject_logical_id not in VpcAttachmentRegistry.__registry[vpc_logical_id]:
            return None

        return VpcAttachmentRegistry.__registry[vpc_logical_id][subject_logical_id]
