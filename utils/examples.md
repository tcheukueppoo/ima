## EXAMPLES

1. In in this context, use `ima` to perform a simple search with google and dump out the results.

```{bash}
ima -s 'OpenBSD'
```

2. Use google engine to search and download 5 pics of Richard Stallman, 1 from each sites it founds.

```{bash}
ima -n 5 -m 1 -a 'Richard stallman'
```

3. Use Duckduckgo to search and download 10 pics of Sia, each pic having a minimum score of 1, save them at '~/artists/sia'.

```{bash}
ima -e duckduckgo -d ~/artists/sia -n 10 -m 2 -o 1 'artists sia'
```

4. Search and pipe download link list of pics of sexy girls to `xargs`.

```{bash}
ima -l '{l}' 'sexy girls' | xargs wget 
```
