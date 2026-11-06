---
name: aws-impersonate
description: Log in to AWS CLI as an IAM user (username + password, optional MFA) with `aws login --remote`, then verify the identity. Use when the user asks to log in to AWS, says the AWS session or credentials expired, or invokes /aws-impersonate. Does not install the CLI and does not use SSO.
---

# AWS impersonate

Log in as an IAM user with browser credentials. Never propose SSO (`aws configure sso`): the user has only username and password. Never install or update the CLI.

## Steps

1. Check the current state:
   ```bash
   aws --version && aws sts get-caller-identity
   ```
   - If `aws` is missing or older than 2.32.0, stop and tell the user: the CLI must be installed first. Do not install it.
   - If `get-caller-identity` already succeeds, report the identity and stop unless the user asked for a fresh login.

2. Have the user run the login. `aws login --remote` waits for a code pasted on stdin, which an agent shell cannot provide, so ask the user to run it in their own terminal:
   ```bash
   aws login --remote --region eu-central-1
   ```
   Tell them what happens:
   - The command prints a URL. Open it on the PC, sign in with username and password (plus MFA if enabled).
   - The browser shows a very long code: copy all of it and paste it into the terminal.

   Use `eu-central-1` unless the user names another region. Add `--profile <name>` only if the user asks for a profile.

3. When the user says it is done, verify:
   ```bash
   aws sts get-caller-identity
   ```
   Report the `Arn` and `Account`.

## Failures

- **Login rejected / AccessDenied on signin**: the IAM user lacks `signin:AuthorizeOAuth2Access` and `signin:CreateOAuth2Token`. Tell the user to ask the AWS account admin to add them.
- **Fallback**: if the user can create access keys, `aws configure` works, but it leaves a permanent key on the machine. Mention the trade-off; do not choose it for them.
- **Expired session later**: credentials are temporary and refresh on their own; when the session finally expires, repeat from step 2.
