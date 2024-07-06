from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from . import forms,models
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib import auth
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date
from django.core.mail import send_mail
from librarymanagement.settings import EMAIL_HOST_USER
# from django.contrib.auth import logout
# from django.urls import reverse
# def user_logout(request):
#     logout(request)
#     return redirect(reverse('login'))

def logout(request):

    # Logout user and redirect to home page
    auth.logout(request)
    return redirect("/")

def home_view(request):
    
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/index.html')



#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/studentclick.html')

#for showing signup/login button for teacher
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/adminclick.html')



def adminsignup_view(request):
    
    form=forms.AdminSigupForm()
    
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()


            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)


            return HttpResponseRedirect('adminlogin')
    return render(request,'library/adminsignup.html',{'form':form})






def studentsignup_view(request):
    
    form1=forms.StudentUserForm()
    
    form2=forms.StudentExtraForm()
    
    mydict={'form1':form1,'form2':form2}
    
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST)
        form2=forms.StudentExtraForm(request.POST)
        
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            user2=f2.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)

        
        return HttpResponseRedirect('studentlogin')
    return render(request,'library/studentsignup.html',context=mydict)




def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

 
def afterlogin_view(request):

    if is_admin(request.user):
        return render(request,'library/adminafterlogin.html')
    else:
        return render(request,'library/studentafterlogin.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)

def addbook_view(request):
    #now it is empty book form for sending to html
    form=forms.BookForm()
    
    if request.method=='POST':
        #now this form have data from html
        form=forms.BookForm(request.POST)
        
        if form.is_valid():
            user=form.save()
            return render(request,'library/bookadded.html')
    return render(request,'library/addbook.html',{'form':form})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)

def deletebook_view(request):
    #now it is empty book form for sending to html
    form=forms.DeleteBookForm()
    
    if request.method=='POST':
        #now this form have data from html
        form=forms.DeleteBookForm(request.POST)
        
        if form.is_valid():
            try:
                isbn_input=form.cleaned_data['isbn']
                
                user=models.Book.objects.get(isbn = isbn_input)
                user.delete()
            except:
                print("record does not exists")    
            return render(request,'library/deletebook.html')
    return render(request,'library/deletebook.html',{'form':form})

 

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)

def viewbook_view(request):
    books=models.Book.objects.all()
    return render(request,'library/viewbook.html',{'books':books})




# @login_required(login_url='adminlogin')
# @user_passes_test(is_admin)

# def issuebook_view(request):
    
#     form=forms.IssuedBookForm()
    
#     if request.method=='POST':
#         #now this form have data from html
#         form=forms.IssuedBookForm(request.POST)
        
#         if form.is_valid():
#             obj=models.IssuedBook()
#             obj.enrollment=request.POST.get('enrollment2')
#             obj.isbn=request.POST.get('isbn2')
#             obj.save()
#             return render(request,'library/bookissued.html')

           
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)

def issuebook_view(request):
    
    form=forms.IssuedBookForm()
    
    if request.method=='POST':
        #now this form have data from html
        form=forms.IssuedBookForm(request.POST)
        
        if form.is_valid():
            obj=models.IssuedBook()
            obj.enrollment=request.POST.get('enrollment2')
            obj.isbn=request.POST.get('isbn2')
            obj.save()
            return render(request,'library/bookissued.html')

    return render(request,'library/issuebook.html',{'form':form})
       

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)

def viewissuedbook_view(request):
    issuedbooks=models.IssuedBook.objects.all()
    li=[]

    for ib in issuedbooks:
        issdate=str(ib.issuedate.day)+'-'+str(ib.issuedate.month)+'-'+str(ib.issuedate.year)
        expdate=str(ib.expirydate.day)+'-'+str(ib.expirydate.month)+'-'+str(ib.expirydate.year)
        #fine calculation
        days=(date.today()-ib.issuedate)
        print(date.today())
        d=days.days
        fine=0
        if d>15:
            day=d-15
            fine=day*10


        books=list(models.Book.objects.filter(isbn=ib.isbn))
        students=list(models.StudentExtra.objects.filter(enrollment=ib.enrollment))
        i=0
        for l in books:
            t=(students[i].get_name,students[i].enrollment,books[i].name,books[i].author,issdate,expdate,fine)
            i=i+1
            li.append(t)


    return render(request,'library/viewissuedbook.html',{'li':li})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)

def viewstudent_view(request):
    students=models.StudentExtra.objects.all()
    return render(request,'library/viewstudent.html',{'students':students})



@login_required(login_url='studentlogin')

def viewissuedbookbystudent(request):
    student=models.StudentExtra.objects.filter(user_id=request.user.id)
    issuedbook=models.IssuedBook.objects.filter(enrollment=student[0].enrollment)

    li1=[]

    li2=[]
    for ib in issuedbook:
        books=models.Book.objects.filter(isbn=ib.isbn)
        for book in books:
            t=(request.user,student[0].enrollment,student[0].branch,book.name,book.author)
            li1.append(t)
        issdate=str(ib.issuedate.day)+'-'+str(ib.issuedate.month)+'-'+str(ib.issuedate.year)
        expdate=str(ib.expirydate.day)+'-'+str(ib.expirydate.month)+'-'+str(ib.expirydate.year)
        #fine calculation
        days=(date.today()-ib.issuedate)
        print(date.today())
        d=days.days
        fine=0
        if d>15:
            day=d-15
            fine=day*10
        t=(issdate,expdate,fine)
        li2.append(t)


    return render(request,'library/viewissuedbookbystudent.html',{'li1':li1,'li2':li2})


def aboutus_view(request):
    return render(request,'library/aboutus.html')


def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message, EMAIL_HOST_USER, ['wapka1503@gmail.com'], fail_silently = False)
            return render(request, 'library/contactussuccess.html')
    return render(request, 'library/contactus.html', {'form':sub})

from django.shortcuts import render
from .models import Book
def book_collection_view(request):
    # Add any logic here if needed
    books = Book.objects.all()
    
    return render(request, 'library/book_collection.html',{'books': books})



from django.shortcuts import render, redirect
from .forms import BookForm
from .models import Book

def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_collection')  # Redirect to the book collection page
    else:
        form = BookForm()
    return render(request, 'add_book.html', {'form': form})


from django.shortcuts import render, redirect
from .models import Book, IssuedBook

def issue_book(request, book_id):
    if request.method == 'POST':
        book = Book.objects.get(pk=book_id)
        issued_book = IssuedBook.objects.create(book=book, borrower_name=request.POST['borrower_name'], return_date=request.POST['return_date'])
        issued_book.save()
        # Optionally, you can delete the book from the Book collection after issuing
        book.delete()
        return redirect('issued_books')
    else:
        book = Book.objects.get(pk=book_id)
        return render(request, 'issue_book.html', {'book': book})
    


@login_required(login_url='studentlogin')

def viewbook_view(request):
    books=models.Book.objects.all()
    return render(request,'library/viewbook.html',{'books':books})


# from django.http import HttpResponse

# def issuebook_view(request):
#     # Your view logic goes here
#     # Make sure to return an HttpResponse object
#    return render(request,'library/viewbook.html')

# views.py

from django.shortcuts import render, redirect
from .models import Book, IssuedBook

def issue_book_view(request):
    if request.method == 'POST':
        # Assuming you have a form with a book ID in the request.POST
        book_id = request.POST.get('book_id')
        book = Book.objects.get(id=book_id)
        # Create an IssuedBook object
        issued_book = IssuedBook(book=book, issued_to=request.user)
        issued_book.save()
        # Redirect to a page displaying issued books
        return redirect('issuedbook')  # Assuming you have a URL named 'issued_books'
    else:
        # Handle GET request if needed
        pass


def issued_books_view(request):
    # Fetch all issued books
    issuedbook = IssuedBook.objects.all()
    return render(request, 'issuedbook.html', {'issuedbook': issuedbook})

