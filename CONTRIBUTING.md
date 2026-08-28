# Contribution workflow

Create feature branches from an updated `main` using short, scoped names such
as `feat/core-grid` or `feat/config-parser`. Keep one Trello card (or one tightly
coupled group) per pull request.

Before requesting review:

1. Rebase or merge the latest `main` as agreed by the team.
2. Run `make lint` and `make test`.
3. Document relevant behavior and decisions.
4. Ask the other teammate for review.
5. Merge only when both teammates can explain the implementation.

Avoid editing unrelated ownership areas in the same pull request. Changes to
shared contracts in `models.py` should be agreed before dependent branches use
them.

