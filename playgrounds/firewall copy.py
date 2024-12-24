#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer

path: str = "/Users/darkmatter/projects/nerd-nest/ts-api"
indexer = AthenahIndexer("local", "id", "dist", "firewall-server", "v1")
indexer.index_dir(path, ["src", "tests"], "firewall-server")

from athenah_ai.client import AthenahClient
from athenah_ai.libs.shell import ShellClient

# prompt0: str = """
# Is there a project.json file in the root of the project? If so, what is the content of the file?
# """
# # client = AthenahClient("id", "dist", "firewall-server")
# # response0 = client.prompt(prompt0)
# # print(response0)


# prompt1: str = """
# List all of the api functions we need to make based on the Controllers. How many Controllers are there? What are all the functions in each Controller?
# """
# # client = AthenahClient("id", "dist", "firewall-server")
# # response1 = client.prompt(prompt1)
# # print(response1)

# response1: str = """
# There are three Controllers: SystemController, UserController, and AuthenticationController. Here are the functions for each Controller:

# 1. **SystemController:**
#    - whitelistAdd
#    - whitelistDelete
#    - blacklistAdd
#    - blacklistDelete

# 2. **UserController:**
#    - users
#    - userByUid
#    - create
#    - sendPasswordResetEmail
#    - passwordReset
#    - sendVerificationEmail
#    - verifyEmail
#    - savePassword
#    - rollbackPassword
#    - save
#    - saveEmail
#    - saveUsername
#    - lockByUid
#    - unlockByUid
#    - deleteByUid
#    - devicesByUid
#    - devicesLogout
#    - devicesDelete
#    - devicesBlock

# 3. **AuthenticationController:**
#    - login
#    - logout
#    - magicLink
#    - magicLinkLogin
#    - idleTimeout
#    - refreshToken
#    - googleAuthCallback
#    - xAuth
#    - xAuthCallback
# """

# task: str = "We need to test the api functions"
# pre_prompt = f"""
# Our current job and sole fucus is to:

# {task}
# """

# prompt2: str = f"""
# {pre_prompt}

# Lets do 3 directories for each controller:

# {response0}

# List the directories and the files we need to create. Return them in a python list.
# """

# client = AthenahClient("id", "dist", "firewall-server")
# response2 = client.prompt(prompt2)
# print(response2)

# code: str = """
# import { setupApp, tearDownApp, IntegrationTestContext } from './setupApp';
# import request from 'supertest';

# describe('authentication.controller.login', () => {
#   let testContext: IntegrationTestContext;
#   const baseUrl = '/api/auth/login';
#   const correctEmail = 'test@example.com';
#   const correctPassword = 'Password123$%!';

#   beforeAll(async () => {
#     testContext = await setupApp();
#   });

#   afterAll(async () => {
#     await tearDownApp(testContext);
#   });

#   it('should return 400 for missing captcha', async () => {
#     const response = await request(testContext.app)
#       .post(baseUrl)
#       .set('Origin', testContext.mock.origin)
#       .set('X-Forwarded-For', testContext.mock.ipAddress)
#       .set('User-Agent', testContext.mock.userAgent)
#       .send({ email: correctEmail, password: correctPassword }); // missing recaptchaResponse

#     // @ts-ignore
#     const responseText = JSON.parse(response.error.text);
#     expect(responseText.message).toBe('BAD_REQUEST');
#     expect(responseText.statusCode).toBe(400);
#     expect(responseText.responseCode).toBe('VALIDATION_ERROR');
#     expect(responseText.errors[0].errorCode).toBe('MISSING_PROPERTY');
#     expect(response.status).toBe(400);
#   });
# });

# import { container } from '../../../src/infrastructure/DIContainer';
# import registerDependencies from '../../../src/config/DIRegistration';
# import App from '../../../src/app';
# import RedisService from '../../../src/services/Redis';
# import { Application } from 'express';
# import sql from 'mssql';

# type APIMockData = {
#   baseUrl: string;
#   origin: string;
#   userAgent: string;
#   ipAddress: string;
# };

# export interface IntegrationTestContext {
#   app: Application;
#   mock: APIMockData;
#   server: any;
#   redis: RedisService;
# }

# export async function setupApp() {
#   registerDependencies();
#   const appInstance = container.resolve<App>('App');
#   await appInstance.initialize();
#   const server = appInstance.app.listen();
#   const redis = appInstance.redisClient();
#   return {
#     app: appInstance.getApp(),
#     server,
#     redis,
#     mock: {
#       baseUrl: '/api',
#       origin: 'https://localhost:3001',
#       userAgent:
#         'Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4472.124 Mobile Safari/537.36',
#       ipAddress: '195.166.157.240',
#     } as APIMockData,
#   } as IntegrationTestContext;
# }

# export async function tearDownApp(testContext: IntegrationTestContext) {
#   try {
#     // Close SQL connection pool
#     if (testContext.app) {
#       // @ts-ignore
#       await sql.close();
#     }

#     // Close Redis client
#     const redisClient = testContext.redis;
#     if (redisClient) {
#       await redisClient.disconnect();
#     }

#     if (testContext.server) {
#       testContext.server.close();
#     }
#   } catch (error) {
#     console.error('Error during shutdown:', error);
#   }
# }

# """
# name: str = "UserController"
# functions: list = [
#     "users",
#     "userByUid",
#     "create",
#     "sendPasswordResetEmail",
#     "passwordReset",
#     "sendVerificationEmail",
#     "verifyEmail",
#     "savePassword",
#     "rollbackPassword",
#     "save",
#     "saveEmail",
#     "saveUsername",
#     "lockByUid",
#     "unlockByUid",
#     "deleteByUid",
#     "devicesByUid",
#     "devicesLogout",
#     "devicesDelete",
#     "devicesBlock",
# ]


# def review(client: AthenahClient, task: str, response2: str, name: str, func: str):
#     response_format: str = """
#     {
#         "result": "final or update",
#         "code": "The code either updated or if it is correct, the same code",
#     }
#     """
#     prompt: str = f"""
#     Goal: {task}
#     Result: {response2}

#     Is this code correct? Is it reaching the goal? If not, return the corrected code.

#     The following must be true.

#     - The code must be in the correct format
#     - The code must be "typed"
#     - The code must have error handling
#     - The code must have docstring (optional) not for testing
#     - The code must have comments (optional) not for testing
#     - THE CODE MUST WORK

#     Return Format:
#     {response_format}

#     Dont not return in code blocks.
#     """

#     response = client.prompt(prompt)
#     print(response)
#     # convert response to python code
#     import ast

#     return ast.literal_eval(response)


def read_file(path: str):
    with open(path, "r") as f:
        return f.read()


def save_code(code_changes: list):
    for content in code_changes:
        print(content)
        file: str = content["file"]
        code: str = content["code"]
        lines = code.split("\n")
        with open(file, "r") as f:
            data = f.readlines()
        updated_data = (
            data[: content["start_line"] - 1] + lines + data[content["end_line"] :]
        )
        with open(file, "w") as f:
            f.writelines("\n".join(updated_data) + "\n")


# def clean(content: str):
#     prompt: str = f"""
#       Does the following code have any blocks or comments that need to be removed?

#       - >>>>>>>>: github merge conflict
#       - <<<<<<<: github merge conflict
#       - ```typescript: code block
#       """
#       client = AthenahClient("id", "dist", "firewall-server")
#       response = client.prompt(prompt)


def build_patch(response: dict):
    prompt: str = f"""
    Build a valid code patch from the following response:
    {response}

    - Do not return in code blocks
    - We will be applying this code using git
    """
    client = AthenahClient("id", "dist", "firewall-server")
    response = client.prompt(prompt)
    print(response)


def worker(base_path: str, testfile: str):
    while True:
        print("Building...")
        ShellClient().do_run(
            "/Users/darkmatter/projects/nerd-nest/firewall-monorepo/ts-api",
            [f"npx prettier --write {testfile}"],
        )
        response = ShellClient().do_run(
            "/Users/darkmatter/projects/nerd-nest/firewall-monorepo/ts-api",
            [f"npm run test:integration {testfile}"],
        )
        # print(response)
        print(f"STD RESPONSE: {response.returncode}")
        # print(f"STD OUT: {response.stdout}")
        print(f"STD ERR: {response.stderr}")
        if f"PASS {testfile}" in response.stderr:
            print("Test Passed")
            break

        full_path: str = f"{base_path}/{testfile}"
        content: str = read_file(full_path)

        return_format: str = """
        [{
            "file": "The file path",
            "start_line": "The start line of the new code",
            "end_line": "The end line of the new code",
            "code": "The diff code changes that will fix the errors",
        }]
        """
        prompt: str = f"""
        Fix the followng errors in this code:

        Code: {content}
        Errors: {response.stderr}
        Path: {full_path}

        - You must return valid typescript code that will fix the errors.
        - Do not return in code blocks or ```typescript
        - You will only return the code that will fix the errors.
        - Insert newlines if needed

        {return_format}
        """

        client = AthenahClient("id", "dist", "firewall-server")
        response = client.prompt(prompt)
        import ast

        code_changes = ast.literal_eval(response)
        save_code(code_changes)


base_path: str = "/Users/darkmatter/projects/nerd-nest/firewall-monorepo/ts-api"
test_path: str = "tests/integration/api/user/create.test.ts"
worker(base_path, test_path)

# for func in functions:

#     prompt3: str = f"""


#   Build the tests to test the api for the following:

#   ```
#   {code}
#   ```

#   Controller: {name}
#   Function: {func}

#   YOU MUST:

#   - Test the failure cases
#   - Test the success cases
#   - Test the edge cases
#   - Test the happy path

#   """

#     client = AthenahClient("id", "dist", "firewall-server")
#     response3 = client.prompt(prompt3)
#     print(response3)
#     while True:
#         review_response = review(client, task, response3, name, func)
#         print(review_response)
#         if review_response["result"] == "final":
#             break

#     save_path: str = (
#         f"/Users/darkmatter/projects/nerd-nest/ts-api/tests/api/{name.lower()}/{func.lower()}.test.ts"
#     )

#     # create the path if it does not exist
#     import os

#     if not os.path.exists(os.path.dirname(save_path)):
#         os.makedirs(os.path.dirname(save_path))

#     with open(save_path, "w") as f:
#         f.write(response3)
#         f.close()
#     print(f"File saved at: {save_path}")
