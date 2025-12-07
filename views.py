from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Student, Department, StudentID
import random


# ---------------------------------------------------
# LIST STUDENTS
# ---------------------------------------------------
@login_required(login_url='/login/')
def student_list(request):
    students = Student.objects.select_related('student_department', 'student_id').all()
    return render(request, 'student_list.html', {'students': students})


# ---------------------------------------------------
# ADD STUDENT
# ---------------------------------------------------
@login_required(login_url='/login/')
def add_student(request):

    departments = Department.objects.all()

    context = {
        "departments": departments,
        "name": "",
        "email": "",
        "age": "",
        "address": "",
        "selected_department": None,
        "employee_id": "",
        "subject": "",
    }

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        age = request.POST.get("age") or 18
        address = request.POST.get("address", "").strip()
        department_id = request.POST.get("department")
        employee_id_input = request.POST.get("employee_id", "").strip()
        subject = request.POST.get("subject", "").strip()

        # Sticky values
        context.update({
            "name": name,
            "email": email,
            "age": age,
            "address": address,
            "selected_department": int(department_id) if department_id else None,
            "employee_id": employee_id_input,
            "subject": subject,
        })

        # Validations
        if not name or not email or not employee_id_input or not subject:
            messages.error(request, "Please fill all required fields.")
            return render(request, 'add_student.html', context)

        if Student.objects.filter(student_email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'add_student.html', context)

        department = Department.objects.filter(id=department_id).first() if department_id else None

        # Create or fetch Student ID
        student_id_obj, created = StudentID.objects.get_or_create(id=employee_id_input)

        # Auto generate marks (50–100)
        marks = random.randint(50, 100)

        # Save student
        Student.objects.create(
            student_name=name,
            student_email=email,
            student_age=age,
            student_address=address,
            student_department=department,
            student_id=student_id_obj,
            student_subject=subject,
            student_marks=marks,
        )

        messages.success(request, "Student added successfully!")
        return redirect('student_list')

    return render(request, 'add_student.html', context)


# ---------------------------------------------------
# EDIT STUDENT
# ---------------------------------------------------
@login_required(login_url='/login/')
def edit_student(request, pk):

    student = get_object_or_404(Student, pk=pk)
    departments = Department.objects.all()
    ids = StudentID.objects.all()

    context = {
        "student": student,
        "departments": departments,
        "ids": ids,
    }

    if request.method == "POST":

        student_name = request.POST.get("name", "").strip()
        student_email = request.POST.get("email", "").strip()
        student_age = request.POST.get("age") or 18
        student_address = request.POST.get("address", "").strip()
        department_id = request.POST.get("department")
        studentid_id = request.POST.get("studentid")

        department = Department.objects.filter(id=department_id).first()
        sid = StudentID.objects.filter(id=studentid_id).first()

        if not department:
            messages.error(request, "Please select a department.")
            return render(request, "edit_student.html", context)

        if not sid:
            messages.error(request, "Please select a valid Student ID.")
            return render(request, "edit_student.html", context)

        # Save data
        student.student_name = student_name
        student.student_email = student_email
        student.student_age = student_age
        student.student_address = student_address
        student.student_department = department
        student.student_id = sid

        student.save()
        messages.success(request, "Student updated successfully!")
        return redirect("student_list")

    return render(request, "edit_student.html", context)


# ---------------------------------------------------
# DELETE STUDENT
# ---------------------------------------------------
@login_required(login_url='/login/')
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect("student_list")


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------
def login_page(request):

    if request.user.is_authenticated:
        return redirect("student_list")

    username_error = ""
    password_error = ""

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(username=username, password=password)

        if user is None:
            password_error = "Invalid username or password."
        else:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect("student_list")

    return render(request, "login1.html", {
        "username_error": username_error,
        "password_error": password_error
    })


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------
@login_required(login_url='/login/')
def logout_page(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("/login/")


# ---------------------------------------------------
# REGISTER
# ---------------------------------------------------
def register(request):

    context = {
        "First": "",
        "Last": "",
        "Username": "",
        "Email": "",
    }

    if request.method == "POST":

        first = request.POST.get("First", "").strip()
        last = request.POST.get("Last", "").strip()
        username = request.POST.get("Username", "").strip()
        email = request.POST.get("Email", "").strip()
        password = request.POST.get("Password", "")

        errors = {}
        password_errors = []

        # Required checks
        if not first:
            errors["first_error"] = "First name is required."
        if not last:
            errors["last_error"] = "Last name is required."
        if not username:
            errors["username_error"] = "Username is required."
        elif User.objects.filter(username=username).exists():
            errors["username_error"] = "Username already taken."

        if not email:
            errors["email_error"] = "Email is required."
        elif User.objects.filter(email=email).exists():
            errors["email_error"] = "Email already registered."

        # Password checks
        special = "!@#$%^&*()-+?_=,<>/"

        if not password:
            password_errors.append("Password is required.")
        else:
            if len(password) < 8:
                password_errors.append("Password must be at least 8 characters.")
            if not any(c.isupper() for c in password):
                password_errors.append("Password must contain an uppercase letter.")
            if not any(c.isdigit() for c in password):
                password_errors.append("Password must contain a number.")
            if not any(c in special for c in password):
                password_errors.append("Password must contain a special character.")

        if password_errors:
            errors["password_errors"] = password_errors

        # Sticky values
        context.update({
            "First": first,
            "Last": last,
            "Username": username,
            "Email": email,
        })

        if errors:
            context.update(errors)
            return render(request, "register1.html", context)

        # Create user
        try:
            user = User.objects.create_user(
                first_name=first,
                last_name=last,
                username=username,
                email=email,
                password=password
            )
            user.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("/login/")
        except IntegrityError:
            messages.error(request, "Error creating your account.")
            return render(request, "register1.html", context)

    return render(request, "register1.html", context)
