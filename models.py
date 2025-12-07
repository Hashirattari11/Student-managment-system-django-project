from django.db import models

class Department(models.Model):
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.department

    class Meta:
        ordering = ['department']


class StudentID(models.Model):
    id = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return self.id


class Student(models.Model):
    student_name = models.CharField(max_length=100)
    student_department = models.ForeignKey(
        Department,
        related_name="depart",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    student_id = models.OneToOneField(
        StudentID,
        related_name="studentid",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    student_email = models.EmailField(unique=True)
    student_age = models.IntegerField(default=18)
    student_address = models.TextField()

    def __str__(self):
        return self.student_name

    class Meta:
        ordering = ['student_name']
        verbose_name = "student"


class Subject(models.Model):
    subject_name = models.CharField(max_length=100)

    def __str__(self):
        return self.subject_name   # FIXED


class subjectMarks(models.Model):   # FIXED class name
    student = models.ForeignKey(Student, related_name="student_marks", on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.IntegerField()

    def __str__(self):
        return f"{self.student.student_name} - {self.subject.subject_name}"

    class Meta:
        unique_together = ('student', 'subject')
