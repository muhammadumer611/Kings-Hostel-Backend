class StudentService:

    def __init__(self):
        self.repository = StudentRepository()
        self.id_generator = StudentIDGenerator()