# flashre tools

## Naming strategies

In practice, the "error" strategy find most of the functions. The "CamelCase"
one only finds few more functions, and some false positives.

```
python -m flashre.main naming ~/Projects/flashre/dumps/w-03/dump_w03-hw.bin --offset 0xC00000
```

```
python -m flashre.main naming ~/Projects/flashre/dumps/w-03/dump_w03-hw.bin --offset 0xC00000 --strategy camelcase
```
