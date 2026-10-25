---
title: "Building Apps, One Problem at a Time: My Journey into Practical Software
  Development"
date: 2026-10-23T23:07:00.000+03:00
description: That means learning how to design a feature, implement it, test it,
  document it, and explain why it exists. It means thinking about the person who
  will use the application, not just the person writing the code. It means
  recognising that accessibility, clear navigation, reliable data handling, and
  understandable interfaces are not extras to be considered after the
  programming is finished. They are part of the product.
image: https://21w441513q.ucarecd.net/04c472e0-a824-402d-8924-aa78f110089b/-/scale_crop/300x300/
---
There is a difference between learning how to write code and learning how to build something that works.

When I started exploring Python, AI tools, and application development, I was interested in the possibilities. I wanted to understand how software is put together, how simple ideas become useful tools, and how technology can solve problems people face in their everyday lives. But the more time I spend building applications, the more I realise that the work goes far beyond writing a few lines of code.

Building an app means making decisions, testing assumptions, finding mistakes, and sometimes undoing changes that seemed like a good idea at first. It means paying attention to details that are easy to overlook when you are only thinking about the finished product. It also means accepting that progress is not always visible. Sometimes, a whole evening of work results in one small improvement. Sometimes, the most useful thing I learn is why something I changed earlier stopped working.

That has become an important part of my experience as I continue learning to build practical digital solutions.

## Learning by building something real

I have reached a point where I do not want my learning to remain limited to exercises, tutorials, and code examples that work only in controlled situations. I want to build applications that have a purpose, can be tested, and might eventually be useful to someone beyond me.

That is one of the reasons I have been working on EduTrack, a school assessment dashboard designed around a practical need: making student assessment information easier to manage and understand.

In a school environment, assessment information is more than a collection of marks. Teachers need ways to record and review results. School administrators need to manage information consistently. Parents need to understand how their children are progressing. A system that helps organise this information can make the process clearer and more manageable.

Working on EduTrack has made me think about software in terms of the people who might use it. It is not enough for a page to load or for a form to accept information. The information must be handled correctly. Invalid marks should not be accepted simply because a user entered them. Different users need access to the functions relevant to their roles. Data must be stored reliably, and the application must behave predictably when something goes wrong.

These requirements have pushed me to look beyond the visible interface and pay attention to the logic underneath it.

I have worked on validation, school and user relationships, assessment records, imports, and the process of preparing the application for online use. Each part introduces its own questions. What happens when a user enters a grade outside the supported range? What happens when a teacher does not have a school assigned? What happens when the database changes from a local file to a production database? How can I test whether a correction has solved the problem without creating another one?

I do not always have the answers immediately. I learn by investigating, testing, and making corrections. That process is becoming just as important to me as the code itself.

## The work does not end when an application runs

One lesson I keep encountering is that getting an application to run is only one stage of development.

An application can work on my computer and still need attention before it is ready for other people. Configuration may differ between development and production. A database may behave differently when hosted online. Environment variables need to be set correctly. A deployment can fail because a required dependency is missing or because the hosting service is looking at the wrong branch of a repository.

I have had to work through these kinds of details while preparing EduTrack for online access. I have learned to pay closer attention to project structure, dependency files, configuration settings, and the relationship between my local environment and the deployed version.

I have also learned to be careful about the data used for demonstrations and testing. A working demonstration should allow someone to explore the application without putting the original project or its data at unnecessary risk.

These may not be the most exciting parts of software development, but they matter. A tool is not useful merely because it exists. It needs to be dependable enough for its intended purpose, and its limitations need to be understood.

I am still developing that judgement. Every problem gives me another reason to slow down, inspect what is happening, and avoid assuming that a successful result in one environment guarantees success everywhere.

## Building my portfolio while learning to build applications

My portfolio has become another part of this journey.

At first, a portfolio can seem like a straightforward task: put together a page, add a few links, describe some projects, and publish it. But I have come to see that a portfolio is itself a small application. It has a structure, navigation, content, visual hierarchy, interactive elements, and a responsibility to present information clearly.

I want my portfolio to show more than a list of technologies I have encountered. I want it to explain the problems I am interested in solving, the projects I am working on, and the kind of developer I am trying to become.

EduTrack is an important part of that story because it connects my interest in programming with a recognisable real-world need. I want visitors to understand that the project is about helping schools organise assessment information and helping parents understand reports and teachers' comments. The point is not simply that I have built a dashboard. It is that I am trying to build something with a purpose.

That has influenced how I think about the portfolio's content and design. I have been refining project descriptions, working on navigation, separating sections into their own pages, and making decisions about how to present my CV and other work.

I have also spent time adjusting the layout so that the interface remains consistent as different projects and descriptions appear. Small details matter here too. A project description that changes the size of a component unexpectedly can make the whole page feel unstable. A navigation link that appears to work but does not lead where expected creates confusion. A CV link needs to take a visitor to the right place and make the document accessible.

These are ordinary interface problems, but they have taught me to think more carefully about the experience of someone using what I build.

## How my communications background shapes my approach

My background in Linguistics, Media and Communication has also influenced the way I approach software development. Communication is not only about what we say; it is also about whether the intended audience can understand the message. I see a similar responsibility in the applications I build. A system may process information correctly, but if its navigation is confusing, its instructions are unclear, or its results are difficult to interpret, the experience is incomplete.

This is particularly important in a project like EduTrack, where assessment information needs to be understandable to teachers, school administrators, and parents with different needs. It also matters in my portfolio and the tools I am developing for myself. I want interfaces to guide people naturally, present information clearly, and make common tasks easier rather than introduce unnecessary complexity.

I am still learning how to translate those principles into design and code, but my communications background gives me a useful perspective: **technology is most useful when people can understand it and use it with confidence.** That is one of the standards I want to keep working towards.

## A small editor that has become a lesson in problem-solving

More recently, I have been building a small local Portfolio Editor to help me manage text in a copy of my website.

The idea is simple. Instead of repeatedly searching through a large HTML file to locate a heading, paragraph, or link, I want an interface that can scan the page's text, group it into categories, let me select an item, and edit it in one place. I also want to preview changes and keep a backup before saving them.

I am building this as a local tool for my copied portfolio, not as a replacement for the live website. Keeping that distinction matters to me because I want to experiment safely without accidentally damaging the version that is already online.

The editor has required me to think about how a web page can be inspected and how its text can be represented in a more manageable form. I have worked on categorising headings, paragraphs, buttons, links, navigation items, and other text. I have also been working on search, selection, editing, and saving changes back to the local HTML file.

The process has not been perfectly smooth.

At one point, I wanted to display additions in green and removed text in red with a strikethrough. The intention was to make changes easier to understand before saving them. But implementing that behaviour introduced new problems. The original text field and the comparison view began behaving like separate fields. The editor stopped accepting continuous typing as expected. Later, duplicate JavaScript declarations caused the script to stop loading, and the category headings disappeared.

These problems were frustrating, but they also made the underlying relationships in the application more visible.

A JavaScript error can prevent an entire section of a page from working, even if the HTML is still present. A function that calculates a difference between two strings is not automatically a good editing interface. A visual change can interfere with the cursor, the text field, or the user's ability to continue typing. A correction that solves one problem can introduce another if the surrounding code is not understood.

I had to trace the problem through the code rather than simply assume the category headings themselves were broken. I checked the category definitions, the function that renders the headings, the HTML containers, and finally the browser console. The console revealed a duplicate declaration of `diffView`, which was preventing the JavaScript from loading correctly.

Removing the duplicate code restored the category headings. That was a useful reminder: sometimes the visible symptom is far away from the actual cause.

The editor is still a work in progress. The automatic comparison needs to work properly alongside direct editing, without creating a second field or interfering with normal typing. I have not finished that part yet. But I now have a clearer understanding of the problem I am trying to solve, and I can return to it with a more specific goal.

That is what I want my development process to become: less about making random changes until something appears to work, and more about understanding the behaviour I want, identifying what is preventing it, and making deliberate corrections.

## Learning to work carefully with code

As a developer, I sometimes have to work with code that I did not write entirely from scratch. I use documentation, examples, development tools, and AI assistance to help me understand unfamiliar sections and move through problems.

I do not see using these resources as a substitute for learning. What matters to me is whether I can understand what a change is intended to do, recognise when it has broken something, test the result, and make a more informed decision the next time.

I am learning that copying a block of code is not the same as understanding where it belongs. The same JavaScript can behave differently depending on the variables available to it, the functions surrounding it, and the way the HTML and CSS are arranged. Even the placement of a closing brace can matter when code is embedded inside a Python string that generates a web page.

I have also learned the value of making smaller changes. When a project is already working in several areas, replacing large sections unnecessarily creates more opportunities for new problems. It is often better to inspect one function, identify one cause, and change only what is needed.

That approach requires patience. It can be tempting to keep editing when something is not right, especially after spending hours trying to get it to work. But a small, verified improvement is more useful than several untested changes whose effects are difficult to separate.

I am trying to become more disciplined about saving my work, checking the browser console, reading server logs, testing the result, and confirming that previously working features still behave as expected.

These habits are not glamorous. They are simply part of learning how to build software responsibly.

## What I am trying to achieve

My aim is to become a developer who can take a practical problem, understand what is needed, and build a tool that helps address it.

I am particularly interested in Python, web applications, automation, and the practical use of AI. I want to understand how these technologies can be used together to reduce repetitive work, organise information, and make everyday processes easier to manage.

I am not approaching this as someone who has already mastered everything. I am still learning the tools, the frameworks, the design decisions, and the habits that make an application reliable. I expect there will be more errors to investigate, more features to revise, and more moments when I have to step back and reconsider an approach.

What I want is to keep moving from isolated exercises towards complete, usable projects.

That means learning how to design a feature, implement it, test it, document it, and explain why it exists. It means thinking about the person who will use the application, not just the person writing the code. It means recognising that accessibility, clear navigation, reliable data handling, and understandable interfaces are not extras to be considered after the programming is finished. They are part of the product.

It also means learning when to stop. Not every feature needs to be added immediately. Sometimes a simpler, stable solution is better than an ambitious feature that introduces more complexity than value. I want to become better at making those decisions as my experience grows.

## Progress is not always dramatic

Much of the work involved in learning software development happens in small increments.

One day, progress might mean getting a deployment to work. Another day, it might mean finding out why a category disappeared from a page. Sometimes it means spending an hour understanding a function before changing it. Other times, it means deciding to leave a problem until the next day rather than continue making changes while tired.

I am learning that this is normal.

The time I put into these projects is not only time spent writing code. It is also time spent investigating errors, understanding unfamiliar concepts, testing different approaches, organising files, checking whether changes have the intended effect, and trying to make an application easier to use.

I want to be honest about that part of the journey because it is easy to look at a finished interface and assume that it came together in a straight line. Usually, the finished result conceals many decisions, corrections, and experiments.

I am not interested in presenting every challenge as a major achievement. Some problems are simply problems that need solving. But I do think the process is worth documenting because it shows how practical development skills are built: through repeated attempts to make something work better, followed by reflection on what those attempts have taught me.

There is value in learning how to recover when something breaks. There is value in understanding why it broke. And there is value in returning to the work with a clearer plan.

## Continuing, one step at a time

For now, I am continuing to develop EduTrack, improve my portfolio, and build small tools that make my own workflow easier. Each project teaches me something different. EduTrack makes me think about users, data, validation, and deployment. My portfolio makes me think about presentation, navigation, and how to communicate my work. The Portfolio Editor makes me think about how to connect backend code, HTML, CSS, and JavaScript in a tool that is both useful and safe to experiment with.

Together, these projects are helping me form a clearer picture of the developer I want to become.

I want to build things that solve actual problems. I want to keep learning how the different parts of an application fit together. I want to become more independent in diagnosing errors and making decisions. And I want to be able to show not only what I have built, but also what I have learned along the way.

I know there is still a great deal to learn. That is not something I need to hide or dress up. It is the reality of where I am in the process.

For me, progress means continuing to show up, working through the problems in front of me, and becoming a little more capable with each project.

I am building applications, but I am also building my understanding of what it takes to make them useful.

That work is ongoing, and I intend to keep at it.
