# Example Session

The following synthetic case demonstrates the intended interaction.

1. The source says a project was delivered in 2022, while a portfolio note says 2023. The skill shows both snippets and asks which date is correct.
2. The source says “improved onboarding” but gives no metric. The skill asks whether the user has a measured result; if not, it proposes the qualitative wording “redesigned the onboarding flow with engineering.”
3. The user confirms the date and approves the qualitative wording. The package records the date as `user_confirmed` and the copy block as `user_approved`.
4. The adapter writes the package into `.resume-site-work/input`; the website builder can now create a site without treating the draft wording as fact.
