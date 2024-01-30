🛸 Overview
---

The `WebPage` object integrates `SessionPage` and `ChromiumPage`, enabling communication between the two.

It can control the browser and send/receive data packets, and synchronizes login information between the two.

It has two modes: d and s, corresponding to controlling the browser and sending/receiving data packets, respectively.

`WebPage` can flexibly switch between these two modes, allowing for interesting use cases.

For example, if the website login code is very complex and using data packets is too complicated, we can use the browser to handle the login and then switch to the data packet mode to collect data.

The logic for using both modes is the same and there is no difference compared to `ChromiumPage`, making it easy to get started.

Diagram of the `WebPage` structure:

![](../imgs/webpage.jpg)

