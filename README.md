# ADN — Symbolic Regression on Android

![Animated demo](assets/demo.svg)
A minimal symbolic regression engine that runs on a smartphone.
No PyTorch. No GPU. No cloud. Just NumPy.

It rediscovers mathematical laws from raw numeric data.

## Results

| Target         | Discovered      | MSE      | Time  |
|----------------|-----------------|----------|-------|
| y = x·sin(x)   | y = x*sin(x)    | 5.36e-33 | 18 ms |
| T = a^(3/2)    | y = a**(3/2)    | 4.77e-31 | 11 ms |

The second is the Third Law of Kepler, rediscovered from numeric
data alone, on a phone, in 11 milliseconds.

## Read the full story

[How I Rediscovered Kepler's Third Law on a Phone, in 204 Lines](https://dev.to/fondation_alpha0az1omega_/how-i-rediscovered-keplers-third-law-on-a-phone-in-204-lines-2hl0)

## Author

**alpha0az1omega**

Built on Termux, Android.
Add animated demo to README
