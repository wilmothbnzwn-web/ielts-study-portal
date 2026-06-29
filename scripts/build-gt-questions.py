#!/usr/bin/env python3
"""
Build General Training (G类) question data from Cambridge IELTS 16 GT PDF extraction.

This script creates:
  1. data/general_reading_tests.json — GT Reading tests
  2. data/general_writing_tasks.json — GT Writing Task 1 & Task 2 prompts

The Cambridge 16 GT PDF content was pre-extracted using pdfplumber.
Answer keys verified against pages 124-131 of the official answer key.

Usage:
  python3 scripts/build-gt-questions.py
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, 'data')

# ── GT Writing Tasks (all 8 from Cambridge 16 GT) ──────────────────

GT_WRITING_TASKS = [
    # ── Test 1 ──
    {
        "id": "gt-cam16-test1-task1",
        "testType": "general",
        "skill": "writing",
        "taskType": "task1",
        "title": "Letter to Mrs Barrett — Help in the Home",
        "prompt": (
            "Mrs Barrett, an English-speaking woman who lives in your town, has "
            "advertised for someone to help her in her home for a few hours a day "
            "next summer.\n\n"
            "Write a letter to Mrs Barrett. In your letter:\n"
            "• suggest how you could help her in her home\n"
            "• say why you would like to do this work\n"
            "• explain when you will and will not be available"
        ),
        "wordLimit": 150,
        "timeMinutes": 20,
        "source": "Cambridge IELTS 16 General Training Test 1",
        "topic": "Everyday Life — Helping at Home",
        "letterType": "semi-formal",
        "salutation": "Dear Mrs Barrett,"
    },
    {
        "id": "gt-cam16-test1-task2",
        "testType": "general",
        "skill": "writing",
        "taskType": "task2",
        "title": "Plastic Pollution — Environment",
        "prompt": (
            "Plastic bags, plastic bottles and plastic packaging are bad for the "
            "environment.\n\n"
            "What damage does plastic do to the environment?\n"
            "What can be done by governments and individuals to solve this problem?\n\n"
            "Give reasons for your answer and include any relevant examples from your own "
            "knowledge or experience."
        ),
        "wordLimit": 250,
        "timeMinutes": 40,
        "source": "Cambridge IELTS 16 General Training Test 1",
        "topic": "Environment"
    },

    # ── Test 2 ──
    {
        "id": "gt-cam16-test2-task1",
        "testType": "general",
        "skill": "writing",
        "taskType": "task1",
        "title": "Letter to Newspaper Editor — Town Centres",
        "prompt": (
            "You have just read an article in a national newspaper which claims that town "
            "centres in your country all look very similar to each other. You don't fully "
            "agree with this opinion.\n\n"
            "Write a letter to the editor of the newspaper. In your letter:\n"
            "• say which points in the article you agree with\n"
            "• explain ways in which your town centre is different from most other town centres\n"
            "• offer to give a guided tour of your town to the writer of the article"
        ),
        "wordLimit": 150,
        "timeMinutes": 20,
        "source": "Cambridge IELTS 16 General Training Test 2",
        "topic": "Everyday Life — Hometown",
        "letterType": "formal",
        "salutation": "Dear Sir or Madam,"
    },
    {
        "id": "gt-cam16-test2-task2",
        "testType": "general",
        "skill": "writing",
        "taskType": "task2",
        "title": "Trying New Things vs Familiar Routines",
        "prompt": (
            "Some people like to try new things, for example, places to visit and types of "
            "food. Other people prefer to keep doing things they are familiar with.\n\n"
            "Discuss both these attitudes and give your own opinion.\n\n"
            "Give reasons for your answer and include any relevant examples from your own "
            "knowledge or experience."
        ),
        "wordLimit": 250,
        "timeMinutes": 40,
        "source": "Cambridge IELTS 16 General Training Test 2",
        "topic": "Society — Lifestyle & Habits"
    },

    # ── Test 3 ──
    {
        "id": "gt-cam16-test3-task1",
        "testType": "general",
        "skill": "writing",
        "taskType": "task1",
        "title": "Letter to Magazine — Book That Influenced You",
        "prompt": (
            "A magazine wants to include contributions from its readers for an article "
            "called 'The book that influenced me most'.\n\n"
            "Write a letter to the editor of the magazine about the book that influenced you "
            "most. In your letter:\n"
            "• describe what this book was about\n"
            "• explain how this book influenced you\n"
            "• say whether this book would be likely to influence other people"
        ),
        "wordLimit": 150,
        "timeMinutes": 20,
        "source": "Cambridge IELTS 16 General Training Test 3",
        "topic": "Everyday Life — Books & Reading",
        "letterType": "formal",
        "salutation": "Dear Sir or Madam,"
    },
    {
        "id": "gt-cam16-test3-task2",
        "testType": "general",
        "skill": "writing",
        "taskType": "task2",
        "title": "Living Close to Where You Were Born",
        "prompt": (
            "Some people spend most of their lives living close to where they were born.\n\n"
            "What might be the reasons for this?\n"
            "What are the advantages and disadvantages?\n\n"
            "Give reasons for your answer and include any relevant examples from your own "
            "knowledge or experience."
        ),
        "wordLimit": 250,
        "timeMinutes": 40,
        "source": "Cambridge IELTS 16 General Training Test 3",
        "topic": "Society — Migration & Home"
    },

    # ── Test 4 ──
    {
        "id": "gt-cam16-test4-task1",
        "testType": "general",
        "skill": "writing",
        "taskType": "task1",
        "title": "Email to Friend — University Accommodation Advice",
        "prompt": (
            "Your friend has been offered a place on a course at the university where you "
            "studied. He/She would like your advice about finding a place to live.\n\n"
            "Write an email to your friend. In your email:\n"
            "• describe where you lived when you were a student at the university\n"
            "• recommend the best way for him/her to look for accommodation\n"
            "• warn him/her of mistakes students make when choosing accommodation"
        ),
        "wordLimit": 150,
        "timeMinutes": 20,
        "source": "Cambridge IELTS 16 General Training Test 4",
        "topic": "Campus Life — Accommodation",
        "letterType": "informal",
        "salutation": "Dear ...,"
    },
    {
        "id": "gt-cam16-test4-task2",
        "testType": "general",
        "skill": "writing",
        "taskType": "task2",
        "title": "Best Time in History to Be Living",
        "prompt": (
            "Some people say that now is the best time in history to be living.\n\n"
            "What is your opinion about this?\n"
            "What other time in history would be interesting to live in?\n\n"
            "Give reasons for your answer and include any relevant examples from your own "
            "knowledge or experience."
        ),
        "wordLimit": 250,
        "timeMinutes": 40,
        "source": "Cambridge IELTS 16 General Training Test 4",
        "topic": "Society — History & Modern Life"
    },
]

# ── GT Reading Tests (Cambridge 16 GT, Test 1 — 3 Sections, 40 Questions) ──

GT_READING_TESTS = [
    {
        "id": "gt-cam16-test1-section1",
        "testType": "general",
        "title": "Helping Pupils Choose Optional Subjects & Ripton Festival",
        "topic": "Education & Community",
        "source": "Cambridge IELTS 16 General Training Test 1 Section 1",
        "difficulty": 2,
        "totalTime": 1200,
        "wordCount": 650,
        "questionCount": 14,
        "main_class": "General Training Reading (G类阅读)",
        "passageText": (
            "<h3>Helping pupils to choose optional subjects when they're aged 14-15: "
            "what some pupils say</h3>"
            "<p><strong>A Krishnan</strong><br>"
            "I'm studying Spanish, because it's important to learn foreign languages and I'm "
            "very pleased when I can watch a video in class and understand it. Mr Peckham "
            "really pushes us, and offers us extra assignments, to help us improve. That's good "
            "for me, because otherwise I'd be quite lazy.</p>"
            "<p><strong>B Lucy</strong><br>"
            "History is my favourite subject, and it's fascinating to see how what we learn about "
            "the past is relevant to what's going on in the world now. It's made me understand "
            "much more about politics, for instance. My plan is to study history at university, "
            "and maybe go into the diplomatic service, so I can apply a knowledge of history.</p>"
            "<p><strong>C Mark</strong><br>"
            "Thursdays are my favourite days, because that's when we have computing. It's "
            "the high spot of the week for me — I love learning how to program. I began when "
            "I was about eight, so when I started doing it at school, I didn't think I'd have any "
            "problem with it, but I was quite wrong! When I leave school, I'm going into my "
            "family retail business, so sadly I can't see myself becoming a programmer.</p>"
            "<p><strong>D Violeta</strong><br>"
            "My parents both work in leisure and tourism, and they've always talked about "
            "their work a lot at home. I find it fascinating. I'm studying it at school, and the "
            "teacher is very knowledgeable, though I think we spend too much time listening "
            "to her; I'd like to meet more people working in the sector, and learn from their "
            "experience.</p>"
            "<p><strong>E Walid</strong><br>"
            "I've always been keen on art, so I chose it as an optional subject, though I was "
            "afraid the lessons might be a bit dull. I needn't have worried, though — our teacher "
            "gets us to do lots of fun things, so there's no risk of getting bored. At the end of "
            "the year the class puts on an exhibition for the school, and I'm looking forward to "
            "showing some of my work to other people.</p>"
            "<hr>"
            "<h3>It's almost time for the next Ripton Festival!</h3>"
            "<p>As usual, the festival will be held in the last weekend of June, this year on "
            "Saturday to Monday, 27-29 June. Ever since last year's festival, the committee has "
            "been hard at work to make this year's the best ever! The theme is <em>Ripton through "
            "the ages</em>. Scenes will be acted out showing how the town has developed since it "
            "was first established. But there's also plenty that's up-to-date, from the latest music "
            "to local crafts.</p>"
            "<p>The Craft Fair is a regular part of the festival. Come and meet professional "
            "artists, designers and craftsmen and women, who will display their jewellery, "
            "paintings, ceramics, and much more. They'll also take orders, so if you want one "
            "of them to make something especially for you, just ask! You'll get it within a month "
            "of the festival ending.</p>"
            "<p>The Saturday barbecue will start at 2 pm and continue until 10 pm, with a "
            "bouncy castle for kids. The barbecue will be held in Palmers Field, or in the town "
            "hall if there's rain. Book your tickets now, as they always sell out very quickly! "
            "Entry for under 16s is free all day; adults can come for free until 6 pm and pay "
            "£5 after that. There'll be live music throughout, with local amateur bands in the "
            "afternoon and professional musicians in the evening.</p>"
            "<p>On Sunday we're delighted to introduce an afternoon of boat races, arranged by "
            "the Ripton Rowing Club. The spectator area by the bridge has plenty of room to "
            "stand and cheer the boats home, in addition to a number of benches. The winners "
            "of the races will be presented with trophies by the mayor of Ripton.</p>"
            "<p>All money raised by the festival will go to support the sports clubs in Ripton.</p>"
        ),
        "questions": [
            # Questions 1-6: Matching pupils to statements
            {"id": 1, "type": "MATCHING", "questionText": "This pupil is interested in the subject despite the way it is taught.", "options": ["A", "B", "C", "D", "E"], "correctAnswer": 3},
            {"id": 2, "type": "MATCHING", "questionText": "This pupil is hoping to have a career that makes use of the subject.", "options": ["A", "B", "C", "D", "E"], "correctAnswer": 1},
            {"id": 3, "type": "MATCHING", "questionText": "This pupil finds the subject harder than they expected.", "options": ["A", "B", "C", "D", "E"], "correctAnswer": 2},
            {"id": 4, "type": "MATCHING", "questionText": "This pupil finds the lessons very entertaining.", "options": ["A", "B", "C", "D", "E"], "correctAnswer": 4},
            {"id": 5, "type": "MATCHING", "questionText": "This pupil appreciates the benefit of doing challenging work.", "options": ["A", "B", "C", "D", "E"], "correctAnswer": 0},
            {"id": 6, "type": "MATCHING", "questionText": "This pupil has realised the connection between two things.", "options": ["A", "B", "C", "D", "E"], "correctAnswer": 1},
            # Questions 7-14: TRUE / FALSE / NOT GIVEN (Ripton Festival)
            {"id": 7, "type": "true_false_not_given", "questionText": "The festival is held every year.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 8, "type": "true_false_not_given", "questionText": "This year's festival focuses on the town's history.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 9, "type": "true_false_not_given", "questionText": "Goods displayed in the craft fair are unlike ones found in shops.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 2},
            {"id": 10, "type": "true_false_not_given", "questionText": "The barbecue will be cancelled if it rains.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 11, "type": "true_false_not_given", "questionText": "Adults can attend the barbecue at any time without charge.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 12, "type": "true_false_not_given", "questionText": "Amateur musicians will perform during the whole of the barbecue.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 13, "type": "true_false_not_given", "questionText": "Seating is available for watching the boat races.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 14, "type": "true_false_not_given", "questionText": "People attending the festival will be asked to donate some money.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 2},
        ]
    },
    {
        "id": "gt-cam16-test1-section2",
        "testType": "general",
        "title": "Reducing Injuries on the Farm & Good Customer Service in Retail",
        "topic": "Workplace & Business",
        "source": "Cambridge IELTS 16 General Training Test 1 Section 2",
        "difficulty": 2,
        "totalTime": 1200,
        "wordCount": 780,
        "questionCount": 13,
        "main_class": "General Training Reading (G类阅读)",
        "passageText": (
            "<h3>Reducing injuries on the farm</h3>"
            "<p>Farms tend to be full of activity. There are always jobs to be done and some "
            "tasks require physical manual work. While it is good for people to be active, there "
            "are risk factors associated with this, and efforts need to be made to reduce them.</p>"
            "<p>The first risk relates to the carrying of an excessive load or weight. This places "
            "undue demands on the spine and can cause permanent damage. Examples of tasks that "
            "involve this risk are moving 50-kilogramme fertiliser bags from one site to another "
            "or carrying heavy buckets of animal feed around fields. According to the UK Health "
            "and Safety Executive, activities such as these 'should be avoided at all times'. Their "
            "documentation states that other methods should be considered, such as breaking down "
            "the load into smaller containers prior to movement or transporting the materials using "
            "a tractor or other vehicle. The risk posed by excessive force is made worse if the "
            "person lifting is also bending over as this increases pressure on the discs in the back.</p>"
            "<p>If a load is bulky or hard to grasp, such as a lively or agitated animal, it will "
            "be more difficult to hold while lifting and carrying. The holder may adopt an awkward "
            "posture, which is tiring and increases the risk of injury. Sometimes a load has to be "
            "held away from the body because there is a large obstacle in the area and the person "
            "lifting needs to be able to see where their feet are going. This results in increased "
            "stress on the back; holding a load at arm's length imposes about five times the stress "
            "of a close-to-the-body position. In such cases, handling aids should be purchased that "
            "can take the weight off the load and minimise the potential for injury.</p>"
            "<p>Another risk that relates to awkward posture is repetitive bending when carrying "
            "out a task. An example might be repairing a gate that has collapsed onto the ground. "
            "This type of activity increases the stress on the back over time. Instead, the gate "
            "could be propped up on a workbench to reduce the need for bending.</p>"
            "<hr>"
            "<h3>Good customer service in retail</h3>"
            "<p>Without customers, your retail business would not exist. It stands to reason, "
            "therefore, that how you treat your customers has a direct impact on your profit margins.</p>"
            "<p>Some customers just want to browse and not be bothered by sales staff. Try to be "
            "sensitive to how much help a customer wants; be proactive in offering help without "
            "being annoying. Suggest a product that naturally accompanies what the customer is "
            "considering or point out products for which there are special offers, but don't pressure "
            "a customer into buying an item they don't want.</p>"
            "<p>Build up a comprehensive knowledge of all the products in your shop, including "
            "the pros and cons of products that are alike but that have been produced under a range "
            "of brand names. If you have run out of a particular item, make sure you know when the "
            "next orders are coming in. Negativity can put customers off instantly. If a customer "
            "asks a question to which the answer is 'no', do not just leave it at that — follow it "
            "with a positive, for example: 'we're expecting more of that product in on Tuesday.'</p>"
            "<p>Meanwhile, if you see a product in the wrong place on a shelf don't ignore it — "
            "put it back where it belongs. This attention to presentation keeps the shop tidy, giving "
            "the right impression to your customers. Likewise, if you notice a fault with a product, "
            "remove it and replace it with another.</p>"
            "<p>When necessary, be discreet. For example, if the customer's credit card is declined "
            "at the till, keep your voice down and enquire about an alternative payment method "
            "quietly so that the customer doesn't feel humiliated. If they experience uncomfortable "
            "emotions in your shop, it's unlikely that they'll come back.</p>"
            "<p>Finally, good manners are probably the most important aspect of dealing with "
            "customers. Treat each person with respect at all times, even when you are faced with "
            "rudeness. Being discourteous yourself will only add more fuel to the fire. Build a "
            "reputation for courteous, helpful service, and your customers will reward you with "
            "their loyalty.</p>"
        ),
        "questions": [
            # Questions 15-20: Table completion (Farm injuries)
            {"id": 15, "type": "COMPLETION", "questionText": "Risk factor: Heavy loads. Reduce risk by dividing into containers that weigh less. Use a vehicle such as a tractor. What should you avoid carrying heavy items of? (Choose ONE WORD from the text)", "correctAnswer": "fertiliser", "wordLimit": 1},
            {"id": 16, "type": "COMPLETION", "questionText": "Awkward posture risk: lifting a restless _____. What animal is mentioned? (ONE WORD)", "correctAnswer": "animal", "wordLimit": 1},
            {"id": 17, "type": "COMPLETION", "questionText": "Moving something around a big _____. (ONE WORD)", "correctAnswer": "obstacle", "wordLimit": 1},
            {"id": 18, "type": "COMPLETION", "questionText": "Buy particular _____ to help with support. (ONE WORD)", "correctAnswer": "aids", "wordLimit": 1},
            {"id": 19, "type": "COMPLETION", "questionText": "A lot of _____ while working, e.g. fixing a fallen gate. (ONE WORD)", "correctAnswer": "bending", "wordLimit": 1},
            {"id": 20, "type": "COMPLETION", "questionText": "Use a workbench instead of bending to fix a fallen _____. (ONE WORD)", "correctAnswer": "gate", "wordLimit": 1},
            # Questions 21-27: Sentence completion (Customer service)
            {"id": 21, "type": "COMPLETION", "questionText": "A _____ approach to selling is fine as long as you do not irritate the customer. (ONE WORD)", "correctAnswer": "proactive", "wordLimit": 1},
            {"id": 22, "type": "COMPLETION", "questionText": "Recommend additional products and _____ without being too forceful. (TWO WORDS)", "correctAnswer": "special offers", "wordLimit": 2},
            {"id": 23, "type": "COMPLETION", "questionText": "Know how to compare similar products which have different _____. (TWO WORDS)", "correctAnswer": "brand names", "wordLimit": 2},
            {"id": 24, "type": "COMPLETION", "questionText": "Avoid _____ by always saying more than 'no'. (ONE WORD)", "correctAnswer": "negativity", "wordLimit": 1},
            {"id": 25, "type": "COMPLETION", "questionText": "Keep an eye on the _____ of goods on the shelves. (ONE WORD)", "correctAnswer": "presentation", "wordLimit": 1},
            {"id": 26, "type": "COMPLETION", "questionText": "If a customer has problems paying with their _____, handle the problem with care. (TWO WORDS)", "correctAnswer": "credit card", "wordLimit": 2},
            {"id": 27, "type": "COMPLETION", "questionText": "Any _____ from a customer should not affect how you treat them. (ONE WORD)", "correctAnswer": "rudeness", "wordLimit": 1},
        ]
    },
    {
        "id": "gt-cam16-test1-section3",
        "testType": "general",
        "title": "Plastic is No Longer Fantastic",
        "topic": "Environment & Business",
        "source": "Cambridge IELTS 16 General Training Test 1 Section 3",
        "difficulty": 3,
        "totalTime": 1200,
        "wordCount": 850,
        "questionCount": 13,
        "main_class": "General Training Reading (G类阅读)",
        "passageText": (
            "<h3>Plastic is no longer fantastic</h3>"
            "<p><strong>A</strong> In 2017, Carlos Ferrando, a Spanish engineer-turned-entrepreneur, "
            "saw a piece of art in a museum that profoundly affected him. 'What Lies Under', a "
            "photographic composition by Indonesian digital artist Ferdi Rizkiyanto, shows a child "
            "crouching by the edge of the ocean and 'lifting up' a wave, to reveal a cluster of "
            "assorted plastic waste, from polyethylene bags to water bottles. The artwork, designed "
            "to raise public awareness, left Ferrando angry and fuelled with entrepreneurial ideas.</p>"
            "<p><strong>B</strong> Ferrando runs a Spanish-based design company, Closca, that "
            "produces an ingenious foldable bicycle helmet. But he has now also designed a stylish "
            "glass water bottle with a stretchy silicone strap and magnetic closure mechanism that "
            "means it can be attached to almost anything, from a bike to a bag to a pushchair "
            "handle. The product comes with an app that tells people where they can fill their "
            "bottles with water for free.</p>"
            "<p><strong>C</strong> The intention is to persuade people to stop buying water in "
            "plastic bottles, thus saving consumers money and reducing the plastic waste piling up "
            "in our oceans. 'Bottled water is now a $100 billion business, and 81 per cent of the "
            "bottles are not recycled. It's a complete waste — water is only 1.5 per cent of the "
            "price of the bottle!' Ferrando cries. Indeed, environmentalists estimate that by 2050 "
            "there will be more plastic in our oceans than fish and that's mainly down to such "
            "bottles. 'We are trying to create a sense that being environmentally sophisticated is "
            "a status symbol,' he adds. 'We want people to clip their bottles onto what they are "
            "wearing, to show that they are recycling — and to look cool.'</p>"
            "<p><strong>D</strong> Ferrando's story is fascinating because it seems like an "
            "indicator of something unexpected. Three decades ago, conspicuous consumption — the "
            "purchase of luxuries, such as handbags, shoes, cars, etc. on a lavish scale — "
            "heightened people's social status. Indeed, the closing decades of the 20th century "
            "were a time when it seemed that consumerism was the dominant value. But increasingly, "
            "particularly with the generation that has grown up online, such behaviour is being "
            "replaced by a new set of values. For many young people today, having the latest "
            "fashionable item is no longer as important as it was to their parents.</p>"
            "<p><strong>E</strong> Ferrando is not alone in this. There is a growing movement "
            "of entrepreneurs who are trying to combine commercial success with environmental "
            "responsibility. These entrepreneurs are betting that consumers — especially younger "
            "ones — will reward companies that align with their values. They believe that the "
            "market for sustainable products is growing rapidly and will continue to expand.</p>"
            "<p><strong>F</strong> It is uncertain whether Closca will succeed in its goal. "
            "Although its foldable bike helmet is available in some outlets in New York, including "
            "the Museum of Modern Art, it can be very hard for any design entrepreneur to really "
            "take off in the global mass market, though not as hard as it might have been in the "
            "past. If an entrepreneur had wanted to fund a smart invention a few decades ago, he "
            "or she would have had to either raise a bank loan, borrow money from a family member "
            "or use a credit card. Things have moved on slightly since then.</p>"
            "<p><strong>G</strong> Entrepreneurs are still using the last two options, but some "
            "are also tapping into the ever-growing pot of money that is becoming available in the "
            "management world for 'corporate social responsibility' (CSR) investments. And then "
            "there are other options for those who wish to raise money straight away. Ferrando "
            "posted details about his water-bottle venture on a large, recognised platform for "
            "funding creative projects. He appealed for people to donate $30,000 of seed money "
            "— the money he needed to get his project going — and promised to give a bottle to "
            "anyone who provided more than $39 in 'donations'. If he received the funds, he stated "
            "that the company would produce bottles in grey and white; if $60,000 was raised, a "
            "multicoloured one would be made. Using this approach, none of the donors has a stake "
            "in his idea, nor does he have any debt. Instead, it is almost a pre-sale of the product, "
            "in a manner that tests demand in advance and creates a potential crowd of enthusiasts. "
            "This old-fashioned community funding with a digital twist is supporting a growing "
            "array of projects ranging from films to card games, videos, watches and so on. And, "
            "at last count, Closca had raised some $52,838 from 803 backers. Maybe, 20 years "
            "from now, it will be the plastic bottle that seems peculiarly old-fashioned.</p>"
        ),
        "questions": [
            # Questions 28-34: Paragraph heading matching
            {"id": 28, "type": "MATCHING", "questionText": "Paragraph A — Choose the correct heading from: i) A time when opportunities were limited ii) The reasons why Fernando's product is needed iii) A no-risk solution iv) Two inventions and some physical details v) The contrasting views of different generations vi) A disturbing experience vii) The problems with replacing a consumer item viii) Looking back at why water was bottled", "options": ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii"], "correctAnswer": 5},
            {"id": 29, "type": "MATCHING", "questionText": "Paragraph B — Choose the correct heading.", "options": ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii"], "correctAnswer": 3},
            {"id": 30, "type": "MATCHING", "questionText": "Paragraph C — Choose the correct heading.", "options": ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii"], "correctAnswer": 1},
            {"id": 31, "type": "MATCHING", "questionText": "Paragraph D — Choose the correct heading.", "options": ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii"], "correctAnswer": 7},
            {"id": 32, "type": "MATCHING", "questionText": "Paragraph E — Choose the correct heading.", "options": ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii"], "correctAnswer": 4},
            {"id": 33, "type": "MATCHING", "questionText": "Paragraph F — Choose the correct heading.", "options": ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii"], "correctAnswer": 0},
            {"id": 34, "type": "MATCHING", "questionText": "Paragraph G — Choose the correct heading.", "options": ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii"], "correctAnswer": 2},
            # Questions 35-37: Multiple choice
            {"id": 35, "type": "CHOICE", "questionText": "What does Ferrando say about his glass water bottle?", "options": ["A It matches his bicycle helmet.", "B It is cheaper than a plastic bottle.", "C He has designed it to suit all ages.", "D He wants people to be proud to show it."], "correctAnswer": 3},
            {"id": 36, "type": "CHOICE", "questionText": "What does the writer find fascinating about Ferrando's story?", "options": ["A the youthfulness of his ideas", "B the old-fashioned nature of his products", "C the choice it is creating for consumers", "D the change it is revealing in people's attitudes"], "correctAnswer": 3},
            {"id": 37, "type": "CHOICE", "questionText": "What does the writer suggest about Closca's bike helmet?", "options": ["A It has both functional and artistic value.", "B Its main appeal is to older people.", "C It has had extraordinary success worldwide.", "D It is a more exciting invention than the glass bottle."], "correctAnswer": 0},
            # Questions 38-40: Summary completion
            {"id": 38, "type": "COMPLETION", "questionText": "Thirty years ago, the methods used by creators to fund their projects involved getting money from the bank or from someone in the _____. (ONE WORD)", "correctAnswer": "family", "wordLimit": 1},
            {"id": 39, "type": "COMPLETION", "questionText": "Ferrando used a well-known _____ to advertise his product and request financial support. (ONE WORD)", "correctAnswer": "platform", "wordLimit": 1},
            {"id": 40, "type": "COMPLETION", "questionText": "Ferrando advised donors that his company would create bottles in two colours, followed by a _____ bottle once they had received a more significant amount. (ONE WORD)", "correctAnswer": "multicoloured", "wordLimit": 1},
        ]
    },
]

# ── Write output files ──

def write_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ {filename} — {len(data) if isinstance(data, list) else sum(len(v) for v in data.values() if isinstance(v,list))} items")
    # Also sync to api/
    api_path = os.path.join(PROJECT_DIR, 'api', filename)
    api_dir = os.path.dirname(api_path)
    if os.path.exists(api_dir):
        with open(api_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"    → synced to api/{filename}")

def main():
    print("Building GT question data...\n")

    # GT Reading: merge into existing reading_tests.json structure
    reading_path = os.path.join(DATA_DIR, 'reading_tests.json')
    with open(reading_path, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    existing_tests = existing.get('tests', [])
    existing_ids = {t['id'] for t in existing_tests}

    new_count = 0
    skip_count = 0
    for gt_test in GT_READING_TESTS:
        if gt_test['id'] in existing_ids:
            print(f"  SKIP (duplicate): {gt_test['id']}")
            skip_count += 1
            continue
        existing_tests.append(gt_test)
        existing_ids.add(gt_test['id'])
        new_count += 1

    existing['tests'] = existing_tests
    write_json('reading_tests.json', existing)
    print(f"  Reading: {new_count} new GT tests added, {skip_count} skipped, total now {len(existing_tests)}\n")

    # GT Writing: standalone file
    write_json('general_writing_tasks.json', GT_WRITING_TASKS)
    print(f"  Writing: {len(GT_WRITING_TASKS)} GT writing tasks created\n")

    print("Done. Restart dev server to pick up changes.")
    print(f"Total GT content: {len(GT_READING_TESTS)} reading tests + {len(GT_WRITING_TASKS)} writing tasks")

if __name__ == '__main__':
    main()
