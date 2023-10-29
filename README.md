# Exchange rate API

## How to use

- install dependencies using poetry
- run `poetry run start`
- respond to prompts

## Thought proccess

So I've decided to create 2 main classes for Graph and Currency.
Also added 3 private helper classes to Currency to make sure that code is organized and SORP is validated
I was thinking of using singletons as it would help with keeping 1 instance but decided against since you could
want to use different separators decimals etc. I've tried to make this code general
so that it could be reusable if someone needed to. Decided against creating class for prompts as
it would be overkill for me since it is a script anyway.