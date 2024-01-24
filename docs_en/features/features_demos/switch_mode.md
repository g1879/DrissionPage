⭐ Mode Switch
---

Log in to the website using a browser and switch to reading the webpage with requests. They will share login information.

```python
from DrissionPage import WebPage
from time import sleep

# Create a page object with the default d mode
page = WebPage()  
# Visit the personal center page (not logged in, redirect to the login page)
page.get('https://gitee.com/profile')  

# Enter the account password to log in
page.ele('@id:user_login').input('your_user_name')  
page.ele('@id:user_password').input('your_password\n')
page.wait.load_start()

# Switch to the s mode
page.change_mode()  
# Output of session mode after login
print('Logged in title:', page.title, '\n')  
```

**Output:**

```shell
Logged in title: Personal Information - Gitee.com
```

