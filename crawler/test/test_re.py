import re

p_string = '<p class="story-body-text story-content">HONG KONG - At the Addiction Treatment Center in eastern</p>'

print p_string

# non-greedy, will match the first '>'
# print re.findall('<p(.*?)>', p_string)
print re.sub(r'<p(.*?)>', "<p class = \"article-body-content\">", p_string)

# greedy, will match all the way to last '>'
p_string = '<p class="story-body-text story-content">Bla bla bla bla</p>'
print "Non greedy:", re.findall('<p(.*?)>', p_string)
print "Greedy:", re.findall('<p(.*)>', p_string)



name = "WILL TIAN"
print name.title()


img_src = 'http://www.newyorker.com/wp-content/uploads/2017/02/Malik-WhyIsSnapCallingItselfaCameraCompany-690.jpg%20690w,%20http://www.newyorker.com/wp-content/uploads/2017/02/Malik-WhyIsSnapCallingItselfaCameraCompany-320.jpg%20320w,%20http://www.newyorker.com/wp-content/uploads/2017/02/Malik-WhyIsSnapCallingItselfaCameraCompany-768.jpg%20768w,%20http://www.newyorker.com/wp-content/uploads/2017/02/Malik-WhyIsSnapCallingItselfaCameraCompany-200.jpg%20200w,%20http://www.newyorker.com/wp-content/uploads/2017/02/Malik-WhyIsSnapCallingItselfaCameraCompany-400.jpg%20400w,%20http://www.newyorker.com/wp-content/uploads/2017/02/Malik-WhyIsSnapCallingItselfaCameraCompany-800.jpg%20800w,%20http://www.newyorker.com/wp-content/uploads/2017/02/Malik-WhyIsSnapCallingItselfaCameraCompany-500.jpg%20500w,%20http://www.newyorker.com/wp-content/uploads/2017/02/Malik-WhyIsSnapCallingItselfaCameraCompany-600.jpg%20600w,%20http://www.newyorker.com/wp-content/uploads/2017/02/Malik-WhyIsSnapCallingItselfaCameraCompany-1000.jpg%201000w,%20http://www.newyorker.com/wp-content/uploads/2017/02/Malik-WhyIsSnapCallingItselfaCameraCompany-1200.jpg%201200w,%20http://www.newyorker.com/wp-content/uploads/2017/02/Malik-WhyIsSnapCallingItselfaCameraCompany-640.jpg%20640w'\

img_src = "http://www.newyorker.com/wp-content/uploads/2017/02/Malik-WhyIsSnapCallingItselfaCameraCompany-690.jpg%20690w,%20http://www."

img_src = re.sub(r'.jpg(.*)', ".jpg", str(img_src))
print img_src