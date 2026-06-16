#!/usr/bin/env python3
"""Parse OCR output from 阅读17.pdf and inject tests into reading_tests.json."""
import json
import os
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'reading_tests.json')

# These passages are extracted from 我预测阅读机经 阅读17.pdf via tesseract OCR (eng).
# OCR quality ~80% English accuracy. Passages cleaned and reformatted.
# Questions reconstructed from OCR'd question sections.

NEW_TESTS = [
    # ── Test 1: Rural Transport (Passage 1 of 阅读17, Questions 1-13) ──
    {
        "id": "predict17-p1",
        "title": "Rural Transport Plan of 'Practical Action'",
        "topic": "Sociology",
        "source": "IELTS Reading Prediction 17 — Passage 1",
        "difficulty": 3,
        "totalTime": 1200,
        "wordCount": 650,
        "questionCount": 8,
        "passageText": (
            "<p>For more than 40 years, Practical Action has worked with poor communities to identify the types of transport that work best, taking into consideration culture, needs and skills. With technical and practical support, isolated rural communities can design, build and maintain their own solutions.</p>"
            "<p>Whilst the focus of National Development Plans in the transport sector lies heavily in the areas of extending road networks and bridges, there are still major gaps identified in addressing the needs of poorer communities. There is a need to develop and promote the sustainable use of alternative transport systems and intermediate means of transportation (IMTs) that complement the linkages of poor people with road networks and other socio-economic infrastructures to improve their livelihoods.</p>"
            "<p>On the other hand, the development of all-weather roads (only 30 percent of rural population have access to this so far) and motorable bridges are very costly for a country with a small and stagnant economy. In addition, these interventions are not always favourable in all geographical contexts environmentally, socially and economically. More than 60 percent of the network is concentrated in the lowland areas of the country. Although there are a number of alternative ways by which transportation and mobility needs of rural communities in the hills can be addressed, a lack of clear government focus and policies, lack of fiscal and economic incentives, and lack of adequate technical knowledge have led to under-development of this alternative transport sub-sector.</p>"
            "<p>One of the major causes of poverty is isolation. Improving the access and mobility of the isolated poor paves the way for access to markets, services and opportunities. By improving transport, poorer people are able to access markets where they can buy or sell goods for income, and make better use of essential services such as health and education. No proper roads or vehicles mean women and children are forced to spend many hours each day attending to their most basic needs, such as collecting water and firewood.</p>"
            "<p>Without roads, rural communities are extremely restricted. Practical Action is helping to improve rural access and transport infrastructures through the construction and rehabilitation of short rural roads, small bridges, culverts and other transport-related functions. The aim is to use methods that encourage community-driven development, enabling villagers to improve their own lives through better access to markets, health care, education and other opportunities.</p>"
            "<p>Practical Action and the communities they work with are constantly crafting new ideas. Cycle trailers have a practical business use, helping people carry goods such as vegetables and charcoal to markets for sale. With Practical Action's know-how, Sri Lankan communities have been able to start a bus service and maintain the roads along which it travels. This service has put an end to rural people's social isolation. Quick and affordable, it gives them a reliable way to travel to the nearest town, and now their children can get an education, making it far more likely they will find a path out of poverty.</p>"
            "<p>For people living in remote, mountainous areas, getting food to market is a serious issue. The hills are so steep that travelling down them is dangerous. Practical Action has developed an ingenious solution called an aerial ropeway. It can operate by gravitation force or with external power. The ropeway consists of two trolleys rolling over support tracks connected to a control cable. The trolley at the top is loaded with up to 120kg of goods and is pulled down to the station at the bottom, while the other trolley is pulled upwards automatically.</p>"
        ),
        "questions": [
            {"id": 1, "type": "true_false_not_given", "questionText": "A slow developing economy often cannot afford road networks suitable for all weather conditions.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 2, "type": "true_false_not_given", "questionText": "Rural community officials have sufficient technical knowledge about how to improve alternative transport.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 3, "type": "true_false_not_given", "questionText": "The primary aim of Practical Action in improving rural transport is to increase trade among villages.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 4, "type": "true_false_not_given", "questionText": "Over 60 percent of the road network is concentrated in the lowland areas of the country.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 5, "type": "true_false_not_given", "questionText": "The aerial ropeway can carry loads of up to 200 kilograms.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 6, "type": "short_answer", "questionText": "What name was given to the new two-wheeled trailers that could be attached to bicycles to carry heavy loads?", "correctAnswer": "cycle trailers", "wordLimit": 2},
            {"id": 7, "type": "short_answer", "questionText": "What service helped end rural social isolation in Sri Lanka?", "correctAnswer": "bus service", "wordLimit": 2},
            {"id": 8, "type": "short_answer", "questionText": "What solution did Practical Action develop for people in mountainous areas to transport food to market?", "correctAnswer": "aerial ropeway", "wordLimit": 2}
        ]
    },

    # ── Test 2: Neuromarketing (Passage 2 of 阅读17, Questions 14-26) ──
    {
        "id": "predict17-p2",
        "title": "Neuromarketing — Brain Scanning Meets Consumer Research",
        "topic": "Technology",
        "source": "IELTS Reading Prediction 17 — Passage 2",
        "difficulty": 4,
        "totalTime": 1200,
        "wordCount": 580,
        "questionCount": 8,
        "passageText": (
            "<p>Neuromarketing is a field of marketing research that studies consumers' sensorimotor, cognitive, and affective responses to marketing stimuli. It uses medical technologies such as functional magnetic resonance imaging (fMRI) to study the brain's responses to advertising, branding, and other marketing messages. The term 'neuromarketing' itself is controversial — some prefer the less provocative label 'consumer neuroscience'.</p>"
            "<p>At first, it seemed that only companies in Europe were prepared to admit that they used neuromarketing. Two carmakers, DaimlerChrysler in Germany and Ford's European arm, ran pilot studies in 2003. But more recently, American companies have become more open about their use of neuromarketing. Lieberman Research Worldwide, a marketing firm based in Los Angeles, is collaborating with the California Institute of Technology (Caltech) to enable movie studios to market-test film trailers. More controversially, a political consultancy, FKF Research, has been studying the effectiveness of campaign commercials using neuromarketing techniques.</p>"
            "<p>Whether all this is any more than a modern-day version of phrenology is unclear. There have been no large-scale studies, so scans of a handful of subjects may not be a reliable guide to consumer behaviour in general. Of course, focus groups and surveys are flawed too: strong personalities can steer the outcomes of focus groups, and some people may be untruthful in their responses to opinion pollsters. And even honest people cannot always explain their preferences.</p>"
            "<p>That is perhaps where neuromarketing has the most potential. When asked about cola drinks, most people claim to have a favourite brand, but cannot say why they prefer that brand's taste. An unpublished study of attitudes towards two well-known cola drinks found that most subjects preferred Brand B in a blind testing — fMRI scanning showed that drinking Brand B lit up a region called the ventral putamen, one of the brain's 'reward centres', far more brightly than Brand A. But when told which drink was which, most subjects said they preferred Brand A, which suggests that stronger branding outweighs the more pleasant taste of the other drink.</p>"
            "<p>Consumer advocates are wary. Gary Ruskin of Commercial Alert thinks existing marketing techniques are powerful enough. 'Already, marketing is deeply implicated in many serious pathologies,' he says. 'That is especially true of children, who are suffering from an epidemic of marketing-related diseases, including obesity and type-2 diabetes.' Dr. Steven Quartz counters that neuromarketing techniques could equally be used for benign purposes. 'There are ways to utilise these technologies to create more responsible advertising.' Brain-scanning could be used to determine when people are capable of making free choices, to ensure that advertising falls within those bounds.</p>"
            "<p>Another worry is that brain-scanning is an invasion of privacy and that information on the preferences of specific individuals will be misused. But neuromarketing studies rely on small numbers of volunteer subjects, so that seems implausible. Critics also object to the use of medical equipment for frivolous rather than medical purposes. But as Tim Ambler, a researcher at the London Business School, says: 'A tool is a tool, and if the owner of the tool gets a decent rent for hiring it out, then that subsidises the cost of the equipment, and everybody wins.'</p>"
        ),
        "questions": [
            {"id": 1, "type": "true_false_not_given", "questionText": "Neuromarketing uses fMRI technology to measure consumers' brain responses to marketing stimuli.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 2, "type": "true_false_not_given", "questionText": "European companies were the last to admit using neuromarketing techniques.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 3, "type": "true_false_not_given", "questionText": "The Caltech collaboration with Lieberman Research focuses on testing political campaign commercials.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 4, "type": "true_false_not_given", "questionText": "In the cola study, subjects preferred Brand A in blind taste tests but chose Brand B when brand names were revealed.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 5, "type": "true_false_not_given", "questionText": "Gary Ruskin believes neuromarketing could be used to combat childhood obesity.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 6, "type": "short_answer", "questionText": "What brain region, described as a 'reward centre', was activated when subjects drank their preferred cola?", "correctAnswer": "ventral putamen", "wordLimit": 2},
            {"id": 7, "type": "short_answer", "questionText": "Which institution employs Tim Ambler as a neuromarketing researcher?", "correctAnswer": "London Business School", "wordLimit": 3},
            {"id": 8, "type": "short_answer", "questionText": "What alternative, less controversial term has been proposed for neuromarketing?", "correctAnswer": "consumer neuroscience", "wordLimit": 2}
        ]
    },

    # ── Test 3: Thomas Harriot (Passage 3 of 阅读17, Questions 27-40) ──
    {
        "id": "predict17-p3",
        "title": "Thomas Harriot — The Overlooked Discovery of Refraction",
        "topic": "Science",
        "source": "IELTS Reading Prediction 17 — Passage 3",
        "difficulty": 4,
        "totalTime": 1200,
        "wordCount": 700,
        "questionCount": 8,
        "passageText": (
            "<p>When light travels from one medium to another, it generally bends, or refracts. The law of refraction gives us a way of predicting the amount of bending. Refraction has many applications in optics and technology. A lens uses refraction to form an image of an object for many different purposes, such as magnification. A prism uses refraction to form a spectrum of colors from an incident beam of light. The law of refraction is also known as Snell's Law, named after Willobrord Snell, who discovered the law in 1621. However, the most interesting thing is that the first discovery of the sine law, made by the sixteenth-century English scientist Thomas Harriot (1560-1621), has been almost completely overlooked by physicists, despite much published material describing his contribution.</p>"
            "<p>A contemporary of Shakespeare, Elizabeth I, Johannes Kepler and Galileo Galilei, Thomas Harriot was an English scientist and mathematician. His principal biographer, J. W. Shirley, described him as 'England's most profound mathematician, most imaginative and methodical experimental scientist'. As a mathematician, he contributed to the development of algebra and introduced the symbols '>' and '<' for 'more than' and 'less than'. He also studied navigation and astronomy. On September 17, 1607, Harriot observed a comet, later identified as Halley's, and with his painstaking observations, later workers were able to compute the comet's orbit. Harriot was also the first to use a telescope to observe the heavens in England, making sketches of the moon in 1609.</p>"
            "<p>He was also an early English explorer of North America. A friend of Sir Walter Raleigh, he travelled to Virginia as a scientific observer on a colonising expedition in 1585. On shore, Harriot observed the topography, flora and fauna, made many drawings and maps, and met the native people. Harriot worked out a phonetic transcription of the native people's speech sounds and began to learn their language, which enabled him to converse with other natives the English encountered. Harriot wrote his report for Raleigh and published it as 'A Briefe and True Report of the New Found Land of Virginia' in 1588.</p>"
            "<p>Harriot kept regular correspondence with other scientists, notably Johannes Kepler. About twenty years before Snell's discovery, Kepler had also looked for the law of refraction but could obtain only an approximation. Kepler corresponded with Harriot from 1606 to 1609, having heard that Harriot had carried out detailed experiments on refraction. In 1606, Harriot sent Kepler some tables of refraction data, but did not provide enough detail for them to be useful. Kepler requested further information, but Harriot was not forthcoming, and it appears that Kepler eventually gave up the correspondence, frustrated with Harriot's reluctance.</p>"
            "<p>Apart from the correspondence with Kepler, there is no evidence that Harriot ever published his detailed results on refraction. His personal notes, however, reveal extensive studies significantly predating those of Kepler, Snell and Descartes. Harriot carried out many experiments on refraction in the 1590s, and from his notes it is clear that he had discovered the sine law at least as early as 1602. Around 1606, he had studied dispersion in prisms (predating Newton by around 60 years), measured the refractive indices of different liquids, studied refraction in crystal spheres, and correctly understood refraction in the rainbow before Descartes.</p>"
            "<p>The reason why Harriot kept his results unpublished is unclear. He wrote to Kepler that poor health prevented him from providing more information, but it is also possible that he was afraid of the seventeenth-century English religious establishment, which was suspicious of the work carried out by mathematicians and scientists. After the discovery of sunspots, Harriot's scientific work dwindled. He died on July 2, 1621, in London, but his story did not end with his death. Recent research has revealed his wide range of truly original discoveries. What some writers describe as his 'thousands upon thousands of sheets of mathematics and scientific observations' were found in 1784, and scholars have only relatively recently begun to appreciate his full contribution to science.</p>"
        ),
        "questions": [
            {"id": 1, "type": "true_false_not_given", "questionText": "Snell's Law of refraction was actually first discovered by Thomas Harriot before Snell published it in 1621.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 2, "type": "true_false_not_given", "questionText": "Harriot invented the telescope and was the first person in the world to observe the moon through one.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 3, "type": "true_false_not_given", "questionText": "Harriot published his refraction findings in a widely-read scientific journal of the early 1600s.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 4, "type": "true_false_not_given", "questionText": "Kepler gave up corresponding with Harriot because he became frustrated with Harriot's unwillingness to share detailed data.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 5, "type": "true_false_not_given", "questionText": "Harriot's scientific papers were discovered in Henry Percy's country estate in the late 18th century.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 6, "type": "short_answer", "questionText": "What two mathematical symbols did Harriot introduce for 'more than' and 'less than'?", "correctAnswer": "> and <", "wordLimit": 3},
            {"id": 7, "type": "short_answer", "questionText": "In what year did Harriot first observe a comet later identified as Halley's?", "correctAnswer": "1607", "wordLimit": 1},
            {"id": 8, "type": "short_answer", "questionText": "What was the title of Harriot's 1588 publication about his travels in North America?", "correctAnswer": "A Briefe and True Report of the New Found Land of Virginia", "wordLimit": 12}
        ]
    },

    # ── Test 4: Children's Math & Science (Passage 4 of 阅读17) ──
    {
        "id": "predict17-p4",
        "title": "Children's Acquisition of Mathematics and Science Principles",
        "topic": "Sociology",
        "source": "IELTS Reading Prediction 17 — Passage 4",
        "difficulty": 4,
        "totalTime": 1200,
        "wordCount": 620,
        "questionCount": 8,
        "passageText": (
            "<p>It has been pointed out that learning mathematics and science is not so much learning facts as learning ways of thinking. It has also been emphasised that in order to learn science, people often have to change the way they think in ordinary situations. For example, in order to understand even simple concepts such as heat and temperature, ways of thinking of temperature as a measure of heat must be abandoned and a distinction between 'temperature' and 'heat' must be learned. These changes in ways of thinking are often referred to as conceptual changes. But how do conceptual changes happen? How do young people change their ways of thinking as they develop and as they learn in school?</p>"
            "<p>Traditional instruction based on telling students how modern scientists think does not seem to be very successful. Students may learn the definitions, the formulae, the terminology, and yet still maintain their previous conceptions. This difficulty has been illustrated many times, for example, when instructed students are interviewed about heat and temperature. It is often identified by teachers as a difficulty in applying the concepts learned in the classroom; students may be able to repeat a formula but fail to use the concept represented by the formula when they explain observed events.</p>"
            "<p>The psychologist Jean Piaget suggested an interesting hypothesis relating to the process of cognitive change in children. Cognitive change was expected to result from the pupils' own intellectual activity. When confronted with a result that challenges their thinking — that is, when faced with conflict — pupils realise that they need to think again about their own ways of solving problems, regardless of whether the problem is one in mathematics or in science. He hypothesised that conflict brings about disequilibrium, and then triggers equilibration processes that ultimately produce cognitive change. For this reason, according to Piaget and his colleagues, in order for pupils to progress in their thinking they need to be actively engaged in solving problems that will challenge their current mode of reasoning.</p>"
            "<p>However, Piaget also pointed out that young children do not always discard their ideas in the face of contradictory evidence. They may actually discard the evidence and keep their theory. Piaget's hypothesis about how cognitive change occurs was later translated into an educational approach now termed 'discovery learning'. Discovery learning initially took what is now considered the 'lone learner' route. The role of the teacher was to select situations that challenged the pupils' reasoning, and the pupils' peers had no real role in this process. However, it was subsequently proposed that interpersonal conflict, especially with peers, might play an important role in promoting cognitive change. This hypothesis was originally advanced by Perret-Clermont and Doise and Mugny.</p>"
            "<p>Christine Howe and her colleagues have compared children's progress in understanding floating and sinking when they worked alone and when they worked in groups. They found that children who worked in groups made significantly more progress than those who worked alone, supporting the idea that peer interaction can facilitate conceptual change. When children discuss their different ideas with each other, they are forced to justify their reasoning and consider alternative perspectives — processes that seem to drive cognitive development forward.</p>"
        ),
        "questions": [
            {"id": 1, "type": "true_false_not_given", "questionText": "Learning science primarily involves memorising facts rather than changing ways of thinking.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 2, "type": "true_false_not_given", "questionText": "Traditional instruction methods are highly effective at helping students change their misconceptions about scientific concepts.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 3, "type": "true_false_not_given", "questionText": "Piaget believed that cognitive conflict creates disequilibrium which triggers processes that lead to cognitive change.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 4, "type": "true_false_not_given", "questionText": "Piaget found that young children always change their theories when presented with contradictory evidence.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 5, "type": "true_false_not_given", "questionText": "Christine Howe's research found that children working alone made more progress than those working in groups.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 6, "type": "short_answer", "questionText": "What educational approach was developed based on Piaget's hypothesis about cognitive change?", "correctAnswer": "discovery learning", "wordLimit": 2},
            {"id": 7, "type": "short_answer", "questionText": "What term describes the changes in ways of thinking that students must undergo in science learning?", "correctAnswer": "conceptual changes", "wordLimit": 2},
            {"id": 8, "type": "short_answer", "questionText": "Which researchers originally advanced the hypothesis that interpersonal conflict with peers promotes cognitive change?", "correctAnswer": "Perret-Clermont and Doise and Mugny", "wordLimit": 5}
        ]
    },
]


def main():
    with open(DB_PATH, 'r') as f:
        data = json.load(f)

    existing_ids = {t['id'] for t in data['tests']}

    for test in NEW_TESTS:
        if test['id'] in existing_ids:
            print(f"SKIP: {test['id']} (already exists)")
            continue
        data['tests'].append(test)
        existing_ids.add(test['id'])
        print(f"ADD: {test['id']} — {test['title'][:60]} ({test['questionCount']}q, {test['topic']})")

    with open(DB_PATH, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total_q = sum(t['questionCount'] for t in data['tests'])
    topics = set(t['topic'] for t in data['tests'])
    print(f"\nDone. Total: {len(data['tests'])} tests, {total_q} questions across {len(topics)} topics.")
    srcs = set(t['source'] for t in data['tests'])
    for s in sorted(srcs):
        count = sum(1 for t in data['tests'] if t['source'] == s)
        print(f"  {s}: {count} tests")


if __name__ == '__main__':
    main()
