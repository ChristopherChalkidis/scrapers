# Attempted Solutions for Headless Mode Triggering Captcha

1. Tried different user agents
Initial user agent set from Funda triggered captcha, but it works when you use the browser agent that your browser is using. You can check this here <https://www.whatismybrowser.com/detect/what-is-my-user-agent/>

2. Tried adding referer
When I initially went to Pararius I used Google and I noticed that Google was set as the referer in the url at that time.
`await page.goto(link, wait_until="domcontentloaded", referer="https://www.google.com")`

3. Random access times
Tried inserting a call to sleep with random times to introduce variety to appear human
`time.sleep(random.random() * 5)`

4. Tried using a different stealth library
`undetected_playwright import stealth_async`
`from playwright_stealth import stealth_async`

5. Changing webdriver
Tried setting webdriver to undefined as recommended on Stackoverflow. The idea behind this is that when you automate a browser it displays webdriver as true and the website's rob detection looks for this. When running in headless mode the code that does this is not triggered because you are not actually automating a browser because there is no browser.

6. Changed referer to Pararius
After getting the captcha while using my vpn I noticed that the url had a referer from Pararius' captcha page so I tried making this the referer.
`await page.goto(link, wait_until="domcontentloaded", referer="https://www.pararius.com/cgi-bin/fl/captcha?q=%252Fenglish")`

7. Set set-ch-ua to match user agent
I found a reference in one of the sites I was browsing to get around bot detection and it mentioned that there something else related to the user agent and they needed to match. My conjecture was that this is why it triggered the Captcha with the old user agent from Funda. Could not find anything regarding how to set this in the headers, it does not appear to be an option using Playwright.
    1. Set-ch-* are called user agent hints. Set-ch-ua tells the site which major version of a browser you're using.

    2. <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Sec-CH-UA>

    3. Idea found on Zenrows <https://www.zenrows.com/blog/bypass-cloudflare#cloudflare-passive-bot-detection-techniques>

# Research Completed

- Captcha was triggered in both headless and headful mode while running my VPN, even when I changed it to appear I was in the Netherlands. I believe this is something to do with the way the traffic appears as it triggers a Captcha when going to Google as well.

- Using Firefox instead of Chromium triggers Captcha even in headful mode.
`browser = await player.firefox.launch(headless=False, timeout=5000)`
`browser = await player.chromium.launch(headless=False, timeout=5000)`

- Possible fingerprinting
Pararius could be using fingerprinting to determine that a vpn is being used. Did not find any helpful information on how to evade this. I thought there may be potential if the fingerprint could be matched to the selected user agent, but did not find a way to set fingerprint. <https://privacycheck.sec.lrz.de/passive/fp_h2/fp_http2.html>
    - Potentially useful information on pages 4, 8, 10.
    - <https://www.blackhat.com/docs/eu-17/materials/eu-17-Shuster-Passive-Fingerprinting-Of-HTTP2-Clients-wp.pdf>
    - Potentially helpful specific to Python
    - <https://www.zenrows.com/blog/what-is-tls-fingerprint>
        - Followed link for Python, but I didn't understand it.
<https://requests.readthedocs.io/en/latest/_modules/requests/adapters/>

- Potential solution by modifying proxies, but I didn't understand fully.
    - <https://requests.readthedocs.io/en/latest/user/advanced/#proxies >
    - <https://free-proxy-list.net/>

- Avoid fingerprinting
    - Zenrows suggested that in order to avoid fingerprinting you should, "Don't make the requests at the same time every day. Instead, send them at random times." Perhaps we should set the time on the bash script to be a random number within a time range.
    - <https://www.zenrows.com/blog/web-scraping-without-getting-blocked#why-is-web-scraping-not-allowed> number 6

- Implement async
    - Attempted to implement async in pararius-get_daily, but it threw an error and couldn't laod the page.
    - <https://www.zenrows.com/blog/speed-up-web-scraping-with-concurrency-in-python>
