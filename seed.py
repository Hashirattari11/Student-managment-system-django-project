from faker import Faker
import random
from .models import *
from home.models import Subject, subject_marks

fake = Faker()

def create_student_marks(n):
    try:
        student_objs = Student.objects.all()
        for student in student_objs:
            subjects = Subject.objects.all()
            selected_subjects = random.sample(list(subjects), k=min(n, len(subjects)))
            for subject in selected_subjects:
                marks = random.randint(0, 100)
                subject_marks.objects.create(
                    student=student,
                    subject=subject,
                    marks=marks
                )
    except Exception as e:
        print(e)

def seed_db(n=10) -> None:
    """
    Seed n students with departments and unique Employee IDs
    """

    # Ensure default departments exist
    default_departments = ["Civil" , "ComputerScience" , "MechanicalEngineering"]
    for dept_name in default_departments:
        Department.objects.get_or_create(department=dept_name)

    departments = list(Department.objects.all())

    for _ in range(n):
        # Faker data
        student_name = fake.name()
        student_email = fake.unique.email()
        student_age = random.randint(18, 49)
        student_address = fake.address()

        # Random department
        department = random.choice(departments)

        # Generate unique Employee ID
        while True:
            employee_id = f'STU-{random.randint(100,9999)}'
            if not StudentID.objects.filter(id=employee_id).exists():
                break

        # Create StudentID object correctly
        student_id_obj = StudentID.objects.create(id=employee_id)

        # Create Student
        Student.objects.create(
            student_name=student_name,
            student_department=department,
            student_id=student_id_obj,
            student_email=student_email,
            student_age=student_age,
            student_address=student_address
        )

    print(f" Successfully seeded {n} students!")
