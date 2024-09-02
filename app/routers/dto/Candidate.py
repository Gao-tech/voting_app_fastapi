from app.models import Applicant


class Candidate:
    def __init__(self):
        self.id = None
        self.name = None

    def assign_from_applicant(self, applicant):
        """Assign id and name from an Applicant instance."""
        if isinstance(applicant, Applicant):
            self.id = applicant.id
            self.name = applicant.fname
        else:
            raise ValueError("Input must be an instance of Applicant class.")