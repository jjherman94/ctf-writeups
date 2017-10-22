# Baby Regex

This challenge gives you a piece of text and a remote service which sends you questions. You have to answer them all to grab the flag. The service asks you to craft regular expressions with constraints that match parts of the given text. Sounds easy right?

Thankfully, you don't actually have to construct any regex on the fly. There are a total of 8 pre-defined questions and each time you connect to the service it gives you one at random. So you can grab them all using a simple script like:
```python
def recon(max_streak=15, wait_duration=5):
    challenges = []
    streak = 0
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect( ('200.136.213.148', 5000) )
        c = recv(client)
        client.close()
        if c in challenges:
            streak += 1
        else:
            challenges.append(c)
            streak = 0
        if streak >= max_streak:
            break
        print '===============streak=%d==============' % streak
        time.sleep(wait_duration)
    return challenges

challenges = recon()
print 'Found %d challenges:\n%s' % (len(challenges), challenges)
```

After that we put them in a list and start studying them. They all require you to match different parts of the text using ridiculous constraints and by imposing a character limit. The engine it uses is python, as mentioned in the description, and the method with which it validates your input is by running it through `re.findall`. Time to open up the [docs](https://docs.python.org/2/library/re.html) and get to work.


```
Type the regex that capture: "Chips" and "code.", and it is only allowed the letter "c" (insensitive)", with max. "15" chars:
```
Starting up with the personal hardest, if we look at the text we see that both `Chips` and `code.` start with `c`, are of length 5 and are located at the end of a sentence. We could try something like `r'(?m)[c|C]....$'` but the constraint prevents us from using any letter other than `c`. Another way is to notice that there is a `,` on the same line for both `Chips` and `code.`, so we could go for something like `r',.+ ([c|C]....)'` but that returns extra results and fixing that will get us over the character limit of 15. Finally, after much frustration and banging head against the wall I ended up with:
```python
challenges[0]: r'c.{3,4},.+ (.+)'
```
If you look closely you will see in both lines we have a `c` character before the `,` either 3 (`card`) or 4 (`cuits`) positions behind. We submit it to the server and it accepts!


```
Type the regex that capture: "All "Open's", without using that word or [Ope-], and no more than one point", with max. "11" chars:
```
This one is also quite tricky. We can see that we have 2 `Open`s, located at the start of the 1st and 3rd line. My immediate reaction was to use the multiline flag to match the start of each line: `r'(?m)^...n'`. Looks good, but we have one `Drin` messing up the results. Again, after much hair-pulling I noticed that the description says we are only not allowed to use *O*. But we could use lowercase *o* instead, by using the ignore case flag! We also have to only use a single point, so we use `\w` in its place:
```python
challenges[1]: r'(?im)^o.\wn'
```
Awesome!


```
Type the regex that capture: "<knowing the truth. >, without using "line break"", with max. "8" chars:
```
This one was quite simple in comparison to the others. Instead of using line break we use the negative group to parse the `\n` character:
```python
challenges[2]: r'<[^>]*>'
```


```
Type the regex that capture: "(BONUS) What's the name of the big american television channel (current days) that matchs with this regex: .(.)\1", with max. "x" chars:
```
Heh. That was a curveball. The `\1` notation references the literal text of the first capture group. In this case that is `(.)`. So, we are looking for something that has the same 2nd and 3rd character:
```python
challenges[3]: r'cnn'
```


```
Type the regex that capture: "FLY until... Fly", without wildcards or the word "fly" and using backreference", with max. "14" chars: 
```
This might confuse you as it did me because there was no way to capture the entire sentence in a group by using backreference, since you can't nest groups in groups! If you use `re.search` instead of `re.findall` you will see that the entire text is parsed under group 0 and the backreference, which will be the word `FLY` is under group 1. We also need to use the `i` flag to ignore case for matching the backreference and we have:
```python
challenges[4]: r'(?i)(F..).+\1'
```
We're even 1 character under the limit!


```
Type the regex that capture: "the follow words: "unfolds", "within" (just one time), "makes", "inclines" and "shows" (just one time), without using hyphen, a sequence of letters (two or more) or the words itself", with max. "38" chars:
```
This one I solved last since it seemed daunting at first, but turned out not so bad. I started by trying to match each word precisely with something like `r'u.f.l.s|w.t.i.|m.k.s|i.c.i.e.|s.o.s'`, but apart from capturing extra words it also captured `within` and `shows` twice. The description states it only needs one match. I then started looking at a pattern in the text around the words in question and I noticed that they were all preceeded by `it`. Great, but what about `unfolds`? Well, turns out you can craft the below regex to also take that into account:
```python
challenges[5]: r'[i|n][t|d] ([^F]...[i|l|s]\w{0,3})'
```
The way I came up with what letters to use for the character groups is I ran it once using only the initial letters of each of the required words, saw which other words matched with the filter and then lined up all the words and looked for similarities in the required ones that were not present in the outliers. And we had 4 characters to spare at the end!


```
Type the regex that capture: "the only word that repeat itself in the same word, using a group called "a" (and use it!), and the group expression must have a maximum of 3 chars, without using wildcards, plus signal, the word itself or letters different than [Pa]", with max. "16" chars: 
```
Looking at the code the only word that repeats itself in the same word is `blabla`, expertly placed within the text :). The solution to that is quite simple, once you know how named groups work:
```python
challenges[6]: r'(?P<a>...)(?P=a)'
```


```
Type the regex that capture: "from "Drivin" until the end of phrase, without using any letter, single quotes or wildcards, and capturing "Drivin'" in a group, and "blue." in another", with max. "16" chars:
```
For this last one, we need to capture the text from the last line, which is a bit similar to the one above it. We use the fact that we can use `-` and that `blue.` is at the very end of the file to write the following regex:
```python
challenges[7]: r'(.{7}).+-(.+)$'
```

And those were all the regex questions! Phew... no idea what that had to do with hacking or computer security but it was damn satisfying writing some pointless regex code golf.

Now all we need to do is package the answers and send them to the server:
```python
def answer(responses):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect( ('200.136.213.148', 5000) )
    while True:
        q = recv(client).lstrip()
        if q in responses:
            print 'Received: %s' % q
            print 'Sending: %s' % responses[q]
            client.send(responses[q]+'\n')
            print recv(client)
        else:
            print q # This outputs the flag
            client.close()
            break
        print '==========================='

answer(responses)
```

