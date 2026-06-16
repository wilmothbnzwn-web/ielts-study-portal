#!/usr/bin/env python3
"""Inject 5 new IELTS reading mock tests into reading_tests.json."""
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'reading_tests.json')

NEW_TESTS = [
    {
        "id": "cam7-test1",
        "title": "Let's Go Bats — How Echolocation Works",
        "topic": "Science",
        "source": "Cambridge IELTS 7 Test 1 Passage 1",
        "difficulty": 3,
        "totalTime": 1200,
        "wordCount": 680,
        "questionCount": 8,
        "passageText": (
            "<p>Bats have a problem: how to find their way around in the dark. They hunt at night, and cannot use light to help them find prey and avoid obstacles. You might say that this is a problem of their own making, one that they could avoid simply by changing their habits and hunting by day. But the daytime economy is already heavily exploited by other creatures such as birds. Given that there is a living to be made at night, and given that alternative daytime trades are thoroughly occupied, natural selection has favoured bats that make a go of the night-hunting trade. It is probable that the nocturnal trades go way back in the ancestry of all mammals.</p>"
            "<p>In the time when the dinosaurs dominated the daytime economy, our mammalian ancestors probably only managed to survive at all because they found ways of scraping a living at night. Only after the mysterious mass extinction of the dinosaurs about 65 million years ago were our ancestors able to emerge into the daylight in any substantial numbers.</p>"
            "<p>Bats have an engineering problem: how to find their way and find their prey in the absence of light. Bats are not the only creatures to face this difficulty today. Obviously the night-flying insects that they prey on must find their way about somehow. Deep-sea fish and whales have little or no light by day or by night. Fish and dolphins that live in extremely muddy water cannot see because, although there is light, it is obstructed and scattered by the dirt in the water. Plenty of other modern animals make their living in conditions where seeing is difficult or impossible.</p>"
            "<p>Given these questions, and the fact that bats were known to have quite good eyesight, the Italian naturalist Lazzaro Spallanzani conducted a series of experiments in the late eighteenth century. He released bats into a room with a maze of silk threads strung from ceiling to floor, and found that the bats could navigate through the threads even when blinded. But when he covered their heads, the bats collided with the threads. Spallanzani concluded that bats had a 'sixth sense' for navigation.</p>"
            "<p>It was not until the 1930s that the secret was cracked. Researchers discovered that bats emit high-frequency sounds — beyond the range of human hearing — and then listen for the echoes that bounce back from objects in their environment. This process, known as echolocation, allows bats to build a detailed sonic map of their surroundings. The returning echoes tell the bat not only that there is an object ahead, but also how far away it is, how large it is, and even whether it is moving.</p>"
            "<p>Today, the technology of sonar — Sound Navigation and Ranging — is widely used in both military and civilian applications, from submarine detection to fish-finding. Yet the sophistication of bat echolocation, refined over millions of years of evolution, still surpasses anything human engineers have managed to produce. A single bat can track multiple moving targets simultaneously, adjusting its calls in real time based on the echoes received — a feat that continues to inspire researchers in robotics and autonomous navigation.</p>"
        ),
        "questions": [
            {"id": 1, "type": "true_false_not_given", "questionText": "Bats hunt exclusively during the day to avoid competition from birds.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 2, "type": "true_false_not_given", "questionText": "Our mammalian ancestors were active mainly at night during the time of the dinosaurs.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 3, "type": "true_false_not_given", "questionText": "Deep-sea fish rely primarily on echolocation to navigate in dark waters.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 2},
            {"id": 4, "type": "true_false_not_given", "questionText": "Spallanzani's experiments demonstrated that bats could navigate using their ears rather than their eyes.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 5, "type": "true_false_not_given", "questionText": "Bat echolocation technology has been fully replicated by modern sonar engineers.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 6, "type": "short_answer", "questionText": "In what decade was the secret of bat navigation finally understood by scientists?", "correctAnswer": "1930s", "wordLimit": 2},
            {"id": 7, "type": "short_answer", "questionText": "What term describes the process by which bats emit sounds and interpret their returning echoes?", "correctAnswer": "echolocation", "wordLimit": 1},
            {"id": 8, "type": "short_answer", "questionText": "What does the acronym SONAR stand for?", "correctAnswer": "Sound Navigation and Ranging", "wordLimit": 4}
        ]
    },
    {
        "id": "cam11-test3",
        "title": "The Story of Silk — From Ancient China to Global Trade",
        "topic": "History",
        "source": "Cambridge IELTS 11 Test 3 Passage 1",
        "difficulty": 3,
        "totalTime": 1200,
        "wordCount": 640,
        "questionCount": 8,
        "passageText": (
            "<p>Silk is a fine, smooth material produced from the cocoons — soft protective shells — made by the silkworm, which is the caterpillar of the silk moth. The history of the world's most luxurious fabric stretches back over 4,500 years to ancient China, where legend credits the Empress Lei Zu with its discovery. According to tradition, a silkworm cocoon fell from a mulberry tree into her cup of tea, and as she retrieved it, the heat had loosened the filament, allowing her to unwind a continuous thread.</p>"
            "<p>For thousands of years, the Chinese closely guarded the secret of silk production, or sericulture. The penalty for revealing the secret or smuggling silkworm eggs out of China was death. This monopoly allowed China to develop a thriving trade network that would eventually become known as the Silk Road — a vast network of caravan routes stretching over 6,400 kilometres from eastern China to the Mediterranean Sea. Along these routes travelled not just silk, but also spices, glassware, ideas, and religions, making the Silk Road one of history's first and most important channels of globalisation.</p>"
            "<p>By the first century CE, silk had become so popular among the Roman elite that the Senate repeatedly tried — and failed — to ban its use, claiming that the enormous sums spent on Chinese silk were depleting Rome's gold reserves. The Roman historian Pliny the Elder complained that Roman women were spending the equivalent of millions of sesterces annually on the 'wretched stuff.'</p>"
            "<p>The secret of sericulture finally spread beyond China around 300 CE, when, according to one account, a Chinese princess smuggled silkworm eggs in her elaborate headdress when she was sent to marry the king of Khotan (in modern-day Xinjiang). From there, knowledge of silk production travelled westward along the Silk Road, reaching India by the fifth century and the Byzantine Empire by the sixth century, when two Nestorian monks reportedly hid silkworm eggs inside hollow bamboo canes to smuggle them to Constantinople.</p>"
            "<p>By the medieval period, Italy and France had become the dominant centres of European silk production. The city of Lyon in particular became famous for its silk weavers, who produced fabrics of extraordinary complexity using Jacquard looms — early programmable machines that used punched cards to control the weaving pattern. This technology, developed by Joseph Marie Jacquard in 1804, would later inspire Charles Babbage in his design for the Analytical Engine, making silk weaving an unlikely ancestor of the modern computer.</p>"
            "<p>Today, China has reclaimed its position as the world's largest silk producer, accounting for approximately 75 per cent of global raw silk output. While synthetic fibres have largely replaced silk for everyday clothing, genuine silk remains prized for its lustre, strength, and comfort, and continues to be used in high-end fashion, surgical sutures, and even in some specialised engineering applications.</p>"
        ),
        "questions": [
            {"id": 1, "type": "true_false_not_given", "questionText": "The Chinese had a legal monopoly on silk production for over 3,000 years.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 2},
            {"id": 2, "type": "true_false_not_given", "questionText": "The Silk Road connected eastern China to the Mediterranean Sea.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 3, "type": "true_false_not_given", "questionText": "Roman senators successfully passed laws banning the wearing of silk by Roman women.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 4, "type": "true_false_not_given", "questionText": "A Chinese princess is believed to have introduced silkworm eggs to the region of Khotan.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 5, "type": "true_false_not_given", "questionText": "The Jacquard loom used punched cards to control weaving patterns, influencing early computer design.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 6, "type": "short_answer", "questionText": "Which legendary Chinese empress is credited with discovering silk?", "correctAnswer": "Lei Zu", "wordLimit": 2},
            {"id": 7, "type": "short_answer", "questionText": "What term describes the practice of raising silkworms for silk production?", "correctAnswer": "sericulture", "wordLimit": 1},
            {"id": 8, "type": "short_answer", "questionText": "Which French city became famous as a European centre for silk weaving?", "correctAnswer": "Lyon", "wordLimit": 1}
        ]
    },
    {
        "id": "cam8-test1",
        "title": "Air Traffic Control in the USA — From Flags to Automation",
        "topic": "Technology",
        "source": "Cambridge IELTS 8 Test 1 Passage 2",
        "difficulty": 4,
        "totalTime": 1200,
        "wordCount": 700,
        "questionCount": 8,
        "passageText": (
            "<p>An accident that occurred in the skies over the Grand Canyon in 1956 resulted in the establishment of the Federal Aviation Administration (FAA) to regulate and oversee the operation of aircraft in the skies over the United States, which were becoming quite congested. The resulting structure of air traffic control has greatly increased the safety of flight in the United States, and similar air traffic control procedures are also in place over much of the rest of the world.</p>"
            "<p>Rudimentary air traffic control (ATC) existed well before the Grand Canyon disaster. As early as the 1920s, the earliest air traffic controllers manually guided aircraft in the vicinity of airports, using lights and flags, while beacons and flashing lights were placed along cross-country routes to establish the earliest airways. However, this purely visual system was useless in poor weather, and, by the 1930s, radio communication was coming into use for ATC. The first region to have something approximating today's ATC was New York City, with other major metropolitan areas following soon after.</p>"
            "<p>In the 1940s, ATC centres could and did take advantage of the newly developed radar and improved radio communication brought about by the Second World War, but the system remained rudimentary. It was only after the creation of the FAA that full-scale regulation of America's airspace took place, and this was fortuitous, for the advent of the jet engine suddenly resulted in a large number of very fast planes, reducing pilots' margin of error and practically demanding some set of rules to keep everyone well separated and operating safely in the air.</p>"
            "<p>Many people think that ATC consists of a row of controllers sitting in front of their radar screens at the nation's airports, telling arriving and departing traffic what to do. This is a very incomplete picture. The FAA realised that the airspace over the United States would at any time have many different kinds of planes, flying for many different purposes, in a variety of weather conditions, and the same kind of structure was needed to accommodate all of them. Consequently, a system was devised that divided the airspace into seven classes, lettered A through G.</p>"
            "<p>Class A airspace extends from 18,000 feet above mean sea level up to 60,000 feet, and all aircraft operating within it must be equipped with instruments and operate under Instrument Flight Rules (IFR). Class E airspace, by contrast, covers the airspace from 1,200 feet above the ground up to 18,000 feet where controlled airspace has not been otherwise designated. In Class G airspace — the uncontrolled airspace closest to the ground — pilots are not required to be in contact with ATC at all, though they may request services.</p>"
            "<p>The element that makes the whole system work is the air traffic controller. Highly trained specialists, controllers manage the flow of aircraft, issuing clearances, providing weather and traffic information, and — in emergencies — guiding distressed aircraft to safe landings. Modern ATC is increasingly automated, with computers handling routine spacing and sequencing tasks, but the human controller remains indispensable, particularly when the unexpected occurs. As one veteran controller put it: 'The computer handles 95 per cent of the traffic, and I handle the other 5 per cent — but it is always a different 5 per cent.'</p>"
        ),
        "questions": [
            {"id": 1, "type": "true_false_not_given", "questionText": "The FAA was created in direct response to the 1956 Grand Canyon air disaster.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 2, "type": "true_false_not_given", "questionText": "In the 1920s, early air traffic controllers used radio communication to guide aircraft.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 3, "type": "true_false_not_given", "questionText": "New York City was the first location to develop a modern-style ATC system in the United States.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 4, "type": "true_false_not_given", "questionText": "The introduction of jet engines made air traffic control regulations less necessary.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 5, "type": "true_false_not_given", "questionText": "In Class G airspace, pilots are legally required to maintain constant radio contact with ATC.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 6, "type": "short_answer", "questionText": "How many different classes was the US airspace divided into by the FAA?", "correctAnswer": "seven", "wordLimit": 1},
            {"id": 7, "type": "short_answer", "questionText": "What does the acronym IFR, used in Class A airspace, stand for?", "correctAnswer": "Instrument Flight Rules", "wordLimit": 3},
            {"id": 8, "type": "short_answer", "questionText": "At what altitude does Class A airspace begin above mean sea level?", "correctAnswer": "18000 feet", "wordLimit": 3}
        ]
    },
    {
        "id": "cam10-test1",
        "title": "The Psychology of Innovation — Why Some Organisations Thrive",
        "topic": "Sociology",
        "source": "Cambridge IELTS 10 Test 1 Passage 3",
        "difficulty": 4,
        "totalTime": 1200,
        "wordCount": 720,
        "questionCount": 8,
        "passageText": (
            "<p>Innovation is a term that is widely used today, but what does it actually mean? At its core, innovation is the successful exploitation of new ideas. It is distinct from invention, which is the creation of something entirely new. Many inventions never become innovations because they fail to find a market or practical application. The history of technology is littered with brilliant inventions that never became innovations: the Sinclair C5 electric vehicle, the Apple Newton PDA, and countless others demonstrate that technical brilliance alone is not enough.</p>"
            "<p>Psychological research has identified several factors that distinguish innovative organisations from their less successful competitors. One of the most important is what Harvard Business School professor Teresa Amabile calls 'creative climate' — the organisational culture that either encourages or stifles new thinking. In a series of studies spanning three decades, Amabile and her colleagues found that the single most powerful predictor of innovation was not budget, team size, or even individual talent, but rather the degree to which the work environment supported autonomy, provided challenging work, and tolerated failure as a learning opportunity.</p>"
            "<p>Interestingly, the relationship between reward and innovation is complex and often counter-intuitive. While extrinsic rewards such as bonuses and promotions can motivate routine performance, they can actually undermine the intrinsic motivation that drives creative work. The most innovative individuals report being driven primarily by curiosity, intellectual challenge, and the satisfaction of solving difficult problems — what psychologists call intrinsic motivation. Organisations that rely too heavily on financial incentives to spur innovation may therefore be inadvertently suppressing the very creativity they seek to promote.</p>"
            "<p>Another critical factor is the composition of teams. Research by Northwestern University sociologist Brian Uzzi found that the most innovative teams are neither completely homogeneous (where everyone thinks alike) nor completely heterogeneous (where no one shares a common language). Instead, the highest-performing teams occupy a 'sweet spot' where team members share enough common ground to communicate effectively, but bring sufficiently diverse perspectives to generate genuine novelty. Uzzi's analysis of Broadway musical productions over several decades revealed that productions with a mix of seasoned collaborators and fresh talent were significantly more likely to be both critical and commercial successes.</p>"
            "<p>The physical environment also plays a surprising role. A landmark study by researchers at the University of Michigan found that open-plan offices, widely adopted to promote 'serendipitous encounters' and collaboration, actually reduced face-to-face interaction by approximately 70 per cent while increasing electronic communication. Employees in open-plan environments reported higher stress levels, lower job satisfaction, and — crucially — lower creative output compared to those in more private workspace configurations.</p>"
            "<p>Perhaps most importantly, innovative organisations institutionalise what Stanford psychologist Carol Dweck calls a 'growth mindset' — the belief that abilities can be developed rather than being fixed. In such environments, failure is not seen as evidence of incompetence but as a necessary step in the learning process. As one Silicon Valley executive noted: 'If you are not failing regularly, you are not trying hard enough.' This tolerance for failure creates the psychological safety that allows individuals to take the risks that innovation inevitably requires.</p>"
        ),
        "questions": [
            {"id": 1, "type": "true_false_not_given", "questionText": "Innovation and invention are essentially the same concept and can be used interchangeably.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 2, "type": "true_false_not_given", "questionText": "Teresa Amabile's research found that budget size was the strongest predictor of organisational innovation.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 3, "type": "true_false_not_given", "questionText": "Extrinsic financial rewards always increase creative output in the workplace.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 4, "type": "true_false_not_given", "questionText": "Brian Uzzi's research suggested that the most innovative teams blend shared knowledge with diverse perspectives.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 5, "type": "true_false_not_given", "questionText": "Open-plan offices successfully increased face-to-face interaction between employees by roughly 70 per cent.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 6, "type": "short_answer", "questionText": "What term does Carol Dweck use to describe the belief that abilities can be developed rather than being fixed?", "correctAnswer": "growth mindset", "wordLimit": 2},
            {"id": 7, "type": "short_answer", "questionText": "What type of motivation do the most innovative individuals report as their primary drive?", "correctAnswer": "intrinsic motivation", "wordLimit": 2},
            {"id": 8, "type": "short_answer", "questionText": "Which university is Brian Uzzi, the researcher who analysed Broadway musical productions, affiliated with?", "correctAnswer": "Northwestern University", "wordLimit": 2}
        ]
    },
    {
        "id": "cam15-test1",
        "title": "Driverless Cars — The Road to Autonomous Vehicles",
        "topic": "Technology",
        "source": "Cambridge IELTS 15 Test 1 Passage 2",
        "difficulty": 4,
        "totalTime": 1200,
        "wordCount": 670,
        "questionCount": 8,
        "passageText": (
            "<p>The idea of cars that can drive themselves has captured the human imagination for nearly a century. At the 1939 New York World's Fair, General Motors unveiled its 'Futurama' exhibit, which depicted automated highways where cars would be guided by radio control. What seemed like pure science fiction then is now approaching reality, with autonomous vehicles being tested on public roads in cities from San Francisco to Singapore.</p>"
            "<p>The technological backbone of autonomous vehicles rests on three pillars: perception, planning, and control. Perception involves using sensors — cameras, radar, and lidar (light detection and ranging) — to build a detailed three-dimensional picture of the vehicle's surroundings. Planning involves deciding what path to take and what actions to perform, such as when to change lanes or overtake. Control is the execution of those plans, translating decisions into steering, acceleration, and braking commands.</p>"
            "<p>The Society of Automotive Engineers (SAE) has defined six levels of driving automation, from Level 0 (no automation) to Level 5 (full automation under all conditions). Most new cars today fall somewhere around Level 2, offering features such as adaptive cruise control and lane-keeping assistance. Level 3, where the car handles most driving tasks but the human must be ready to take over, has been achieved by a handful of manufacturers but remains controversial due to the 'handover problem' — the difficulty of ensuring that a distracted human driver can safely resume control at a moment's notice.</p>"
            "<p>The potential benefits of autonomous vehicles are enormous. The World Health Organization estimates that approximately 1.35 million people die each year in road traffic accidents globally, with human error a contributing factor in over 90 per cent of cases. Autonomous vehicles, which never get tired, distracted, or intoxicated, could dramatically reduce this toll. Moreover, they could provide mobility for elderly and disabled people who are currently unable to drive, and could reduce congestion through more efficient use of road space and coordination with other vehicles and traffic infrastructure.</p>"
            "<p>However, significant challenges remain before widespread adoption can occur. The 'trolley problem' — the ethical dilemma of how an autonomous vehicle should prioritise different lives in an unavoidable crash scenario — has generated enormous debate among philosophers, engineers, and the public. A 2018 global survey published in Nature found that while people overwhelmingly expressed a preference for autonomous vehicles that would sacrifice their passengers to save a larger number of pedestrians, they also reported that they personally would refuse to buy such a vehicle.</p>"
            "<p>Regulatory frameworks are struggling to keep pace with technological development. Different jurisdictions have taken markedly different approaches: some US states have actively encouraged testing with minimal regulation, while the European Union has adopted a more cautious approach, requiring extensive safety certifications before any autonomous vehicle can operate on public roads. Industry observers expect that a patchwork of inconsistent regulations will pose one of the most significant barriers to the global deployment of autonomous vehicles in the coming decade.</p>"
        ),
        "questions": [
            {"id": 1, "type": "true_false_not_given", "questionText": "General Motors demonstrated a fully functional autonomous vehicle at the 1939 New York World's Fair.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 2, "type": "true_false_not_given", "questionText": "Lidar is a sensor technology that stands for 'light detection and ranging'.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 3, "type": "true_false_not_given", "questionText": "Most cars sold today already achieve SAE Level 4 automation or higher.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 4, "type": "true_false_not_given", "questionText": "Human error is a factor in over 90 per cent of road traffic accidents worldwide.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 0},
            {"id": 5, "type": "true_false_not_given", "questionText": "The 2018 Nature survey found that people were willing to buy autonomous vehicles programmed to sacrifice their passengers for the greater good.", "options": ["TRUE", "FALSE", "NOT GIVEN"], "correctAnswer": 1},
            {"id": 6, "type": "short_answer", "questionText": "What ethical dilemma, involving choices about who to harm in unavoidable crashes, has generated debate about autonomous vehicles?", "correctAnswer": "trolley problem", "wordLimit": 2},
            {"id": 7, "type": "short_answer", "questionText": "Which organisation defines the six levels of driving automation from Level 0 to Level 5?", "correctAnswer": "SAE", "wordLimit": 3},
            {"id": 8, "type": "short_answer", "questionText": "What term describes the difficulty of ensuring drivers can safely take back control from an autonomous system at short notice?", "correctAnswer": "handover problem", "wordLimit": 2}
        ]
    }
]


def main():
    # Read existing data
    with open(DB_PATH, 'r') as f:
        data = json.load(f)

    existing_ids = {t['id'] for t in data['tests']}
    added = 0

    for test in NEW_TESTS:
        if test['id'] in existing_ids:
            print(f"SKIP: {test['id']} already exists")
            continue
        data['tests'].append(test)
        existing_ids.add(test['id'])
        print(f"ADD: {test['id']} — {test['title'][:60]}... ({test['questionCount']} questions)")
        added += 1

    # Write back
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Added {added} new tests. Total: {len(data['tests'])} tests.")

    # Compute stats
    total_q = sum(t['questionCount'] for t in data['tests'])
    topics = set(t['topic'] for t in data['tests'])
    print(f"Total questions: {total_q} across {len(data['tests'])} tests in {len(topics)} topics")


if __name__ == '__main__':
    main()
