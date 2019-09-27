""" Splitting a sentence by ending characters """

import re

st1 = "  Another example!! Let me contribute 0.50 cents here?? \
         How about pointer '.' character inside the sentence? \
         Uni Mechanical Pencil Kurutoga, Blue, 0.3mm (M310121P.33). \
         Maybe there could be a multipoint delimiter?.. Just maybe...  "
st2 = "One word"


def split_sentences(st):
    st = st.strip() + '. '
    sentences = re.split(r'[.?!][.?!\s]+', st)
    return sentences[:-1]

print(split_sentences(st1))
print(split_sentences(st2))
