import re

p_string = '<p class="story-body-text story-content">HONG KONG - At the Addiction Treatment Center in eastern</p>'

print p_string

# non-greedy, will match the first '>'
# print re.findall('<p(.*?)>', p_string)
print re.sub(r'<p(.*?)>', "<p class = \"article-body-content\">", p_string)

# greedy, will match all the way to last '>'
# print re.findall('<p(.*)>', p_string)



name = "WILL TIAN"
print name.title()