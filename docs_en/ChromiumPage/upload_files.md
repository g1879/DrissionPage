🚤 File Upload
---

There are two ways to upload a file:

- Find the `<input>` element and insert the file path.

- Intercept the file input box and automatically fill in the path.

## ✅️️ Traditional Method

The first method is the traditional method, where developers need to find the file upload control in the DOM and use the `input()` method of the element object to insert the path.

The file upload control is an `<input>` element with the `type` attribute set to `'file'`, and the file path can be entered into the element. Its usage is the same as entering text.

The only difference is that

