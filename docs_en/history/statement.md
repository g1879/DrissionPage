Self-Introduction
---

## ✅️ Introduction

A few years ago, there was a very strange system.

Its business logic was extremely peculiar, the interface design was incomprehensible, the runtime speed varied and the error handling was inconsistent.

Unfortunately, this system had to hold several events every year, and everyone who used it complained about it.

Even more unfortunately, I was one of the administrators of this system.

Every time an event was held, the phone on my desk would ring off the hook every day.

In order to process the collected data, I had to ask several interns to manually organize it for a week.

In short, it was a tool that caused productivity to regress.

Unable to bear it any longer, I started learning automation to save myself from the heavy and laborious work.

---

## ✅️ Getting Started and Development

I searched online and found that Selenium was the most popular web automation tool at the time, so I began learning and using it, embarking on the path of automation.

At first, I felt that Selenium was amazing. With just a dozen lines of code, I could accomplish tasks that used to take me half a day.

As I delved deeper into my understanding, I gradually felt that Selenium was like a shell of a house. It only provided the most basic tools, but to use them, I had to do a considerable amount of encapsulation myself. So I learned the POM (Page Object Model) pattern and started working on my own page objects.

However, as a beginner, I was at a loss when encountering various strange error messages, and didn't know how to deal with various unstable situations. There were even some pre-existing pitfalls that were difficult to handle. During this time, I encountered countless obstacles, spent countless efforts, and encountered and overcome numerous challenges.

Gradually, the tools I encapsulated became more mature. With the increase in usage scenarios, there were also more requirements.

---

## ✅️ Birth

Based on my experience and requirements, I summarized the following needs:

Firstly, the statements in Selenium were too verbose. Implicit waits had a narrow scope of application, explicit wait statements were overly complex, element search statements were lengthy, and chain operations were unsightly, making it unbearable for me as a minimalist.

Secondly, the element search methods were not user-friendly. This was the most commonly used operation, but it was often written in long and cumbersome ways. I wanted to create a concise and efficient syntax for element searching.

Additionally, I wanted to combine browsers with requests, leveraging their strengths to achieve a balance between writing speed and execution speed.

Finally, I had already encapsulated a batch of useful methods and filled in many of Selenium's own pitfalls. I wanted to be able to conveniently use my handy tools wherever I went.

Therefore, this library was born.

Drission is a term I coined. It is a combination of the first half of "Driver" and the second half of "Session".

Because the object that controls the browser in Selenium is called `WebDriver`, and the object used for sending and receiving data packets in requests is called `Session`, Drission is an attempt to combine them.

And Page represents the library in units of pages, encapsulating it using the POM pattern.

---

## ✅ Version Iteration

Although I have a foundation in programming and front-end development, I am also self-taught in Python, so it's like feeling my way across a river.

Fortunately, the project-driven learning method has progressed quickly. Whatever the project needs, I learn that knowledge. It's like completing a puzzle, gradually filling in various knowledge gaps.

At the beginning, there were many things I didn't understand, so I used existing libraries. Versions v0.x to v1.4 were based on Selenium and requests-html. Selenium was responsible for controlling the browser, and requests-html was responsible for sending and receiving packets.

During this phase, I achieved unification of the APIs for controlling the browser and sending/receiving packets, interoperability of cookies, and established the basic usage logic.

However, using requests-html as the underlying layer was a bit too heavy. After gradually understanding its operating principles, I refactored this part of the underlying code using requests and lxml. This brought me to the second phase.

The second phase was from v1.5 to v2.x. The browser control part still relied on Selenium, while the packet sending/receiving and parsing functions were completely self-developed. During this phase, running the program felt much easier, and I was able to add more useful features and optimizations. However, the bottleneck shifted to Selenium.

The more I used it, the deeper my understanding became, and my dissatisfaction with Selenium grew. Selenium was restricted by chromedriver, and many of my ideas could not be implemented. For example, it was unable to take screenshots of entire web pages; or when switching between tabs, previously obtained elements would become invalid; or downloading the corresponding chromedriver for different versions of the browser, which could result in being unable to use newer versions of the browser due to lack of a new driver, and so on.

There is another important point. In recent years, our country has been suppressed by the Americans in various ways. I already had a sense of frustration and wanted to contribute a small amount to the domestic open source community.

So I arrived at the third phase.

After 2-3 years of use, I encountered enough pitfalls and gained some insights into automation. With a mindset of giving it a try, I boldly took a step towards developing my own underlying technology. In version 3.x, DrissionPage completely eliminated its reliance on Selenium and conducted a complete overhaul of the underlying infrastructure.

Once I made up my mind to develop my own technology, a whole new world opened up. Breaking free from the constraints of the chromedriver framework, I suddenly felt a sense of liberation. From then on, DrissionPage not only runs faster than Selenium, but it also enables various technological innovations. Those who have used it should have experienced this, so I won't dwell on it here.

By the way, it's worth mentioning that DrissionPage has an unexpected side effect. It can actually pass through human-machine detection tools like cloudflare and Google. This is something even the author didn't anticipate. Perhaps it's because DrissionPage is a niche creation that these big companies are not familiar with.

---

## ✅ Random Thoughts

For some reason, after version 3.x, the previously obscure DrissionPage has suddenly become popular. Gitee even granted it a GVP. The stars on GitHub have been steadily increasing. It's a pleasant surprise, and I'm grateful for everyone's support.

In fact, the author is a very laid-back developer. Development is not their main profession, and building libraries is just a hobby. Truth be told, as additional features were added, many of them were not even used by the author. Continuing to develop is mostly driven by interest. This is a piece of work that the author has carefully crafted, hoping to make it as perfect as possible. The code I've written is running in the world, like an extension of my own life. More importantly, I feel that I've made a small contribution to the software industry in our country, and that makes it meaningful.

However, automated software can often be a double-edged sword. Here, as the author, I have to put on armor. Please do not use DrissionPage for any work that may violate laws or ethical constraints. Please use DrissionPage responsibly, adhere to the spider protocol, and do not use it for any illegal purposes. By choosing to use DrissionPage, you are agreeing to this agreement. The author assumes no responsibility for any legal risks or losses resulting from your violation of this agreement, and you bear all the consequences.

Finally, returning to the beginning, the system that once disgusted me has been greatly improved by a responsible development team. Although it had a rough start, they actively participated in the business and continuously iterated the product. After several major updates, the system is now incredibly useful. Therefore, I have high hopes for Chinese software and believe it will continue to improve in the future.

