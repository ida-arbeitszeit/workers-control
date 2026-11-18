How to Contribute
=================


Translating the app
-------------------

We want people around the world to use the workers control app.
To achieve this, it's crucial to translate the app into as many languages as possible.
If you are a translator and would like to support us, please contact us.
We are happy to help you with the translation process.
No technical knowledge is required.


Contributing code
------------------

We appreciate contributions to the code! Before you start contributing, you'll need to set up your development environment. The setup process is
detailed in our :doc:`getting_started` guide.

You can propose changes by `forking the repository <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo>`_ and creating a pull request on GitHub.
Before submitting changes, run ``./run-checks`` to ensure your code meets our standards.

Squash commits that belong together into one. Make sure that PRs are small enough
to be reviewed. If you propose a large change, split it into several PRs, for example
by first implementing the core, then the web and finally the Flask layer.

If you introduce changes that may be relevant to users, operators or providers of the app,
add an entry under "Unreleased" in CHANGELOG.md describing the change
(without referencing an issue or pull request ID).

Changes created with the help of LLMs are held to the same standards of code quality
and reviewability as code written by humans: PRs must not be too large for a human review,
and the code must be understandable and as clean as possible, without redundant comments.


Working on Milestones
-----------------------

Milestones are our way of organizing larger work packages (>50h of work) that have been identified as important for the project. Unlike regular Issues or Pull Requests, milestones follow a formal approval process that includes an obligatory RFC (Request For Comments). This structured approach helps us plan better and ensures that all developers are aligned with the project's direction.

.. rubric:: Milestone Lifecycle
    :heading-level: 3

1. RFC Candidate
    - An Issue on GitHub that has potential to become a Milestone
    - Marked with the "rfc candidate" label
    - Requires initial conceptual work and discussion
    - View `current candidates <https://github.com/ida-arbeitszeit/workers-control/issues?q=state%3Aopen%20label%3A%22rfc%20candidate%22>`_

2. RFC (Request For Comments)
    - A detailed proposal marked with the "RFC" label
    - Must include a motivation for the change and a detailed implementation proposal
    - Sent to the programmers mailing list for visibility
    - Requires approval in an app group meeting
    - View `current RFCs <https://github.com/ida-arbeitszeit/workers-control/issues?q=is%3Aissue%20state%3Aopen%20label%3Arfc>`_

3. Active Milestone
    - Published on GitHub after RFC approval
    - Ready for implementation
    - View `all milestones <https://github.com/ida-arbeitszeit/workers-control/milestones>`_

Feel free to contribute to any of these stages.
