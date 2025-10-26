# Admin Panel Management Guide

## Accessing Django Admin

1. Start your Django server:
   ```
   python manage.py runserver
   ```

2. Navigate to: `http://127.0.0.1:8000/admin/`

3. Login with your superuser credentials

## Managing Admin Users

### Creating/Editing Admin User

1. Go to Django Admin Panel
2. Click on **"Users"** in the list
3. To create a new admin user:
   - Click **"Add User"** or **"Add"** button
   - Enter username and password
   - Check **"Staff status"** and **"Superuser status"** checkboxes
   - Save

4. To edit existing admin user:
   - Find the user in the list (e.g., username "admin")
   - Click on the username
   - You can change:
     - **Username**
     - **Password** (set a new password)
     - **Email**
     - **First name** and **Last name**
     - **Staff status** (required for admin access)
     - **Superuser status** (gives full admin privileges)

### Resetting Admin Password

1. Go to Django Admin
2. Click on **Users**
3. Find the admin user
4. Click on their username
5. Scroll to the **"Password"** section
6. Click **"Change password"**
7. Set a new password
8. Click **"Save"**

### Setting Up the Default Admin User

To set up the admin user with username "admin" and password "dadah06!":

1. Go to `http://127.0.0.1:8000/admin/`
2. Click **"Users"**
3. Click **"Add"** button
4. Fill in:
   - **Username:** admin
   - **Password:** dadah06!
   - Check ✅ **Staff status**
   - Check ✅ **Superuser status**
5. Click **"Save"**

Now you can login to your app at the main login page with:
- Username: admin
- Password: dadah06!

## Features Available in Admin Panel

### Users Management
- View all users
- Edit user details
- Change passwords
- Manage user permissions (Staff, Superuser, Active status)
- View user profiles

### Educational Sections
- Add/edit educational content
- Manage sections by category
- Upload attachments and images

### Festival Events
- Create and manage events
- Filter by event type and date
- Upload event images

## Security Tips

1. **Change the default password** if you've created the admin user programmatically
2. **Use strong passwords** for admin accounts
3. **Limit superuser status** to only necessary accounts
4. **Regularly review user permissions** in the admin panel


