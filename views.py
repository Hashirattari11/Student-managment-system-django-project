from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Student, Department, StudentID



# -----------------------------
# LIST STUDENTS
# -----------------------------
@login_required(login_url='/login/')
def student_list(request):
    students = Student.objects.select_related('student_department', 'student_id').all()
    return render(request, 'student_list.html', {'students': students})

# -----------------------------
# ADD STUDENT
# -----------------------------
@login_required(login_url='/login/')
def add_student(request):
    departments = Department.objects.all()

    context = {
        'departments': departments,
        'name': '',
        'email': '',
        'age': '',
        'address': '',
        'selected_department': None,
        'employee_id': '',
    }

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        age = request.POST.get('age') or 18
        address = request.POST.get('address', '').strip()
        department_id = request.POST.get('department')
        employee_id_input = request.POST.get('employee_id', '').strip()

        # Preserve sticky values
        context.update({
            'name': name,
            'email': email,
            'age': age,
            'address': address,
            'selected_department': int(department_id) if department_id else None,
            'employee_id': employee_id_input
        })

        # Validations
        if not name or not email or not employee_id_input:
            messages.error(request, "Please fill all required fields.")
        elif Student.objects.filter(student_email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            department = Department.objects.filter(id=department_id).first() if department_id else None

            # Create or get Employee ID object
            student_id_obj, created = StudentID.objects.get_or_create(id=employee_id_input)

            # Create student
            Student.objects.create(
                student_name=name,
                student_email=email,
                student_age=age,
                student_address=address,
                student_department=department,
                student_id=student_id_obj
            )
            messages.success(request, "Student added successfully!")
            return redirect('student_list')

    return render(request, 'add_student.html', context)
    
# -----------------------------
# EDIT STUDENT
# -----------------------------
@login_required(login_url='/login/')
def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    departments = Department.objects.all()
    ids = StudentID.objects.all()

    context = {
        'student': student,
        'departments': departments,
        'ids': ids,
    }

    if request.method == "POST":
        student_name = request.POST.get('name', '').strip()
        student_email = request.POST.get('email', '').strip()
        student_age = request.POST.get('age') or 18
        student_address = request.POST.get('address', '').strip()
        department_id = request.POST.get('department')
        studentid_id = request.POST.get('studentid')

        department = Department.objects.filter(id=department_id).first() if department_id else None
        sid = StudentID.objects.filter(id=studentid_id).first() if studentid_id else None

        # Validation
        if not department:
            messages.error(request, "Please select a department.")
        elif not sid:
            messages.error(request, "Please select a valid Employee ID.")
        else:
            student.student_name = student_name
            student.student_email = student_email
            student.student_age = student_age
            student.student_address = student_address
            student.student_department = department
            student.student_id = sid
            student.save()
            messages.success(request, "Student updated successfully!")
            return redirect('student_list')

    return render(request, 'edit_student.html', context)

# -----------------------------
# DELETE STUDENT
# -----------------------------
@login_required(login_url='/login/')
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect('student_list')

# -----------------------------
# LOGIN
# -----------------------------
def login_page(request):
    if request.user.is_authenticated:
        return redirect('/student_list/')

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
            return redirect('/student_list/')

    context = {
        "username_error": username_error,
        "password_error": password_error
    }
    return render(request, "login1.html", context)

# -----------------------------
# LOGOUT
# -----------------------------
@login_required(login_url='/login1/')
def logout_page(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('/login1/')

# -----------------------------
# REGISTER
# -----------------------------
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

        # Field validations
        if not first:
            errors["first_error"] = "First name is required."
        if not last:
            errors["last_error"] = "Last name is required."
        if not username:
            errors["username_error"] = "Username is required."
        elif Student.objects.filter(username=username).exists():
            errors["username_error"] = "Username already taken."
        if not email:
            errors["email_error"] = "Email is required."
        elif Student.objects.filter(email=email).exists():
            errors["email_error"] = "Email already registered."

        # Password validations
        special_characters = "!@#$%^&*()-+?_=,<>/"
        if not password:
            password_errors.append("Password is required.")
        else:
            if len(password) < 8:
                password_errors.append("Password must be at least 8 characters long.")
            if not any(c.isupper() for c in password):
                password_errors.append("Password must contain at least one uppercase letter.")
            if not any(c.isdigit() for c in password):
                password_errors.append("Password must contain at least one number.")
            if not any(c in special_characters for c in password):
                password_errors.append("Password must contain at least one special character.")

        if password_errors:
            errors["password_errors"] = password_errors

        # Preserve form data
        context.update({
            "First": first,
            "Last": last,
            "Username": username,
            "Email": email
        })

        if errors:
            context.update(errors)
            return render(request, "register1.html", context)

        # Create user
        try:
            user = Student.objects.create_user(
                first_name=first,
                last_name=last,
                username=username,
                email=email,
                password=password
            )
            user.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('/student_list/')
        except IntegrityError:
            messages.error(request, "Something went wrong while creating your account.")
            return render(request, "register1.html", context)
    return render(request, "register1.html", context)
