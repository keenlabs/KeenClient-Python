# Keen IO Python Client

First off, thank you for considering contributing to this official Keen IO client. It's people like you that make Keen IO such a great tool.

We put these guidelines together to try and make working with our SDK as straight forward as possible, and hopefully help you understand how we communicate about potential changes and improvements.

Improving documentation, bug triaging, building modules for various frameworks or writing tutorials are all examples of helpful contributions we really appreciate.

Please, don't use the issue tracker for support questions. If you have a support question please come hang out in our Slack  at http://keen.chat or send an email to team@keen.io.

## Guidelines

* Create issues for any major changes and enhancements that you wish to make. Discuss things transparently and get community feedback.
* Be welcoming to newcomers and encourage diverse new contributors from all backgrounds. See the [Python Community Code of Conduct](https://www.python.org/psf/codeofconduct/).

## Your First Contribution

Here are a couple of friendly tutorials with more information about contributing to OSS projects: 

- http://makeapullrequest.com/,
- http://www.firsttimersonly.com/
-[How to Contribute to an Open Source Project on GitHub](https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github)
- [Github's Open Source Guide](https://opensource.guide)

At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first :smile_cat:

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.

### Run the following commands to get this project installed locally

```ssh
$ git clone https://github.com/keenlabs/KeenClient-Python && cd KeenClient-Python
# Make sure you're in a python virtual environment before installing
$ python setup.py develop

# Run tests locally
$ python setup.py test
```

### Submitting a Pull Request

Use the template below. If certain testing steps are not relevant, specify that in the PR. If additional checks are needed, add 'em! Please run through all testing steps before asking for a review.

```
## What does this PR do? How does it affect users?

## How should this be tested?

Step through the code line by line. Things to keep in mind as you review:
 - Are there any edge cases not covered by this code?
 - Does this code follow conventions (naming, formatting, modularization, etc) where applicable?

Fetch the branch and/or deploy to staging to test the following:

- [ ] Does the code compile without warnings (check shell, console)?
- [ ] Do all tests pass?
- [ ] If the feature sends data to Keen, is the data visible in the project if you run an extraction (include link to collection/query)?
- [ ] If the feature saves data to a database, can you confirm the data is indeed created in the database?

## Related tickets?
```

This PR template can be viewed rendered in Markdown [here](./.github/PULL_REQUEST_TEMPLATE.md). Github will auto-populate any new PRs filed with this template, so don't worry about copy-pasting it.

## How to report a bug
If you find a security vulnerability, do NOT open an issue. Email team@keen.io instead.

If you find a bug that's not a security vulnerability please head over to the issues tab of this rep and open up an issue.

We created these labels to help us organize issues: 

-`bugs`
-`docs`
-`enhancements`
-`feature-request`

Please use them when creating an issue where it makes sense!

## Suggesting features

We welcome your feedback and requests. If you have a straight forward request please open up an issue that details the request. If you want to talk to someone on the Keen team head over to http://keen.chat or send a note to team@keen.io and we will make sure and get you in touch with the product team.

# Code review process

The core team looks at Pull Requests and issues on a regular basis and will typically respond within 5 business days.

<!-- Template based on Dustin Larimer's CONTRIBUTING.md for the Keen IO Javascript Client: https://github.com/keen/keen-js/blob/master/CONTRIBUTING.md -->