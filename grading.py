# grading
import re
from typing import Callable, Tuple

from src.utils import ask_gpt

_GRADER_SYSTEM = (
    "You are an expert writing instructor. "
    "Follow the given rubric exactly to grade essay and return ONLY the final score, nothing else."
)

RUBRIC = """
After reading each essay and completing the analytical rating form, assign a holistic score based on the rubric below. For the following evaluations you will need to use a grading scale between 1 (minimum) and 6 (maximum). As with the analytical rating form, the distance between each grade (e.g., 1-2, 3-4, 4-5) should be considered equal.

##SCORE OF 6: An essay in this category demonstrates clear and consistent mastery, although it may have a few minor errors. A typical essay effectively and insightfully develops a point of view on the issue and demonstrates outstanding critical thinking, using clearly appropriate examples, reasons, and other evidence to support its position; the essay is well organized and clearly focused, demonstrating clear coherence and smooth progression of ideas; the essay exhibits skillful use of language, using a varied, accurate, and apt vocabulary and demonstrates meaningful variety in sentence structure; the essay is free of most errors in grammar, usage, and mechanics.

### Example essay with a score of 6:
 Cell Phones are now seen as an essential item for millions of people. Throughout each day people need to use their phones for multiple reasons including, communicating with family members, answering phone calls from work, or using the GPS to drive to the nearest McDonalds. Smartphones make life simpler and even safer, but that is not always the case. Most people lack the discipline to peel away from their phone when put in situations where multitasking is not a good idea. For example, while driving the steering wheel needs all of your attention because a simple glance at your phone trying to text back your mom could cause a fatal accident. It is evident that texting while driving should be banned or at least states should be willing to put major restrictions to reduce the dangerous outcomes from using an electronic device while driving a vehicle. People should not be allowed to use their cell phones at any time while driving a vehicle because they are putting themselves at a higher risk to crash, cellsphones reduce the drivers ability to maintain focus, and phones are the leading cause of accidents in the highway.

People should not be allowed to use their cellphones while driving at any time due to the fact that it increases the likelihood of a car wreck. It is true, people all over the world are super busy and never enough time to get things done so they try to multitask. This leaves them to get things done while on the road. Most Americans are addicted to their phone as well and check their phone more times then needed while driving. According to a study made last year, "People who text while driving are 6 times more likely to get into an accident than those who drive while intoxicated." While this may seem crazy, something illegal such as drinking and driving is less dangerous than texting and driving but, it is a fact that cannot be ignored. Even though millions are told to not text and drive they continue to ignore the deadly warnings from participating in cellphone use while operating a vehicle yet once again making the wrong choice. Always remember that texting or using a cellphone while driving is extremely risky not only for yourself but for those in your car as well as vehicles around you.

In 2009, 5,474 lives were taken and 448,000 people got injured from car accidents from being distracted while driving, as stated by the government. The lives of innocent people are being taken every day because of a simple distraction. Car crashes are four times more common to take place while the driver is on their phones over any other causes. Different states have views on the laws that are being used about texting while driving. Utah has a law established stating that if a driver is texting while driving and crashes they will spend fifteen years in jail. Most people don't seem to realize how careless they can be while driving a car. Talking on a cell phone is not as dangerous as texting these days. While talking on the phone, it is easier to still keep focused on the road in front of the driver. When they look at their text messages, it's not possible to look in both directions at once, therefore all of their focus goes straight to the screen of the cell phone. The article "10 Terryfying facts about texting and driving'' by Drivers Alert states, "11 teenagers die every day due to texting and driving. Teenagers are 400% more likely to get into an accident from texting and driving. AT&T's Teen Driver Survey found that 97% of teenagers think it's dangerous, while 43% of them engage in the activity anyway." It's hard for all drivers, especially teenagers, to put down the cell phone and put their hands on the wheel, which results in many car crashes. That means the carelessness of any driver could end their life in seconds or even worse cause the death of others. While driving, the driver's main focus should never be their phone; it should be getting to their destination safely.

Texting and driving is the leading cause of crashes on the road. Most would imagine that it would be reckless driving by intoxicated people but that is not true. As stated previously, only 11 teenagers die every day due to the use of cellphones while driving and that doesnt even include adults or other bystanders. Hence, the reason why most states and countries have declared cellphone use while driving illegal. Unfortunately, the rate of crashes caused by cell phone use has only gone down 4%. Furthermore, did you know that 1 out of 4 people die from crashes that are involved with cellular device usage. Most of you would agree that you are a good driver and that texting does not impact your driving skills, but statistics show otherwise. Imagine a scenario, where you are driving and receive a text from your mother and all you have to do is respond yes or no. Studies have shown that it takes a person at least 5 seconds to reply. If you were going 55 miles per hour that's like driving half a the length of a football field. Anything could happen in those 5 seconds and this is probably the case in most crashes every single day making this one of the leading causes in the world.

There is no question, vehicles and cell phones both are definitely important objects in every person's life. Sometimes people even use both at the same time just because they can without thinking about the consequences. Bad things will always come from cellphone usage while operating a vehicle. No matter how many laws are placed, tools made to lessen the contact between you and your phone the only actual way to not allow your phone to distract you is to put it away. It is understandable, if there is an emergency and you need to pick up the phone but, if it's just a text from your mom with no urgency all you have to do is simply wait. It only takes considering the possibilities of terrible things that can happen by choosing to prioritize your safety as well as others. It is never too hard to practice using your phone less while driving, and most importantly if you have children or teens who see you on your phone while driving they might think it's okay to do it as well. In that case you might not crash that day, but in the future your kids who saw you do it choose to do it as well. There are various ways and solutions to make cell phone usage close to none, use them to keep yourself safe. So, next time your phone rings, make sure to send the right message by not sending that text.


## SCORE OF 5: An essay in this category demonstrates reasonably consistent mastery, although it will have occasional errors or lapses in quality. A typical essay effectively develops a point of view on the issue and demonstrates strong critical thinking, generally using appropriate examples, reasons, and other evidence to support its position; the essay is well organized and focused, demonstrating coherence and progression of ideas; the essay exhibits facility in the use of language, using appropriate vocabulary demonstrates variety in sentence structure; the essay is generally free of most errors in grammar, usage, and mechanics.
### Example essay with a score of 5:
Should Drivers use Cell phones while driving?

What would we do without the latest technologies in our daily life? We use computers for work and in school, we use cell phones to access apps and do research. At home, we use microwaves to heat up food and landlines have been replaced by cell phones as the main phone of many people. In our daily lives we use cell phones to text, look up boarding passes, check flights and make phone calls. More and more, people are using technology, including cell phones, as an important part of their lives. As more and more people become dependent on the use of cell phones, some of the time they are being used may be in a car, while driving. Is the cell phone more helpful or hurtful when they are used by drivers in a car?

While a small minority of people do not have cell phones, the prevalence of cell phone ownership and use has increased. "Cell phone usage is becoming a mounting issue in the United States with 91% of Americans (97% of people between 18-24) owning cell phones and using them for texting, calling and communicating for personal, work and school in daily life." ("Cell Phone ownership"). Cell phones are so in trend with their convenience and popularity they seem to be increasing in numbers and not decreasing. "Eighty-one percent of Americans own smart phones up from 35% in the 2011" ("Mobile Fact Sheet"). It seems that more people are becoming dependent on them, despite the potential risks. For teens, texting has become more popular as making a phone call. Starting in the year 2001, State governments have started creating laws to limit cell phone usage by individuals driving in cars, as risks arise.

Despite the controversy there are benefits of cellphones especially for teenage students, who are now using new technologies during the school year. Cell phones are becoming more popular in school as a learning aid. "In a recent poll 94% of students use their phones in class for learning" ("Cell phone use"). The Majority of U.S. students are now relying on cell phones to get their school assignments and homework done. Since these teens have the cell phones in their possession, as they drive to school, they may be tempted to use them, both texting and calling, while they are behind the wheel. The benefits of this immediate communication with others and the convenience it creates, it may be outweighed by the risks and dangers of this usage.

In contrast to the benefits for cell phones, the dangers of distracted driving are real. Starting in the 2000's, States have started to restrict the use of cell phones while driving mainly due to the incidence of car accidents involving a driver using their cell phone. The fatalities do not just include the driver, but also the passengers and other victims. "Twenty states, Washington D.C. and Puerto Rico have hand-held cell phone use bans and thirty-eight states ban all cell phone use by novice and teen drivers" ("Distracted Driving Laws"). "Cell phone use while driving causing distracted driving has been linked to automobile accidents and fatalities". ("Distracted Driving Laws"). The increase in accidents associated with cell phones is still controversial and there are arguments on both sides as far as the causes.

Some surprising emerging data shows a benefit of cell phones is their use in emergency situations. "Patients are more likely to survive when emergency services are called from a cell phone rather than a landline" (Weinlich). "It is associated with improved mortality rates at the scene of medical events" ("Mobile Phones proven"). Drivers may use their cell phones while driving to report an emergency. As more people continue to use cell phones more people may be able to helped and potentially saved in emergencies. Is the risk of distracted driving worth the potential benefit of helping someone in distress?

In addition to the risk associated with distracted driving there is another health risk associated with phone use. "Cell phones give off a form of energy known as radiofrequency (RF) waves." ("Cell Phone Safety"). And while this risk occurs whether the person is driving or not, it would be another reason for the driver to adhere to the handsfree laws. The concern has been a link that shows increasing risk of brain tumors of the head and neck while the driver holds the phone to the face (Creagan). "The evidence is mixed though and there is limited evidence linking cell phone radiation to human cancer" ("Electromagnetic Fields"). The mounting risks and seeming benefits for the driver are numerous and careful consideration must be used when considering using a cell phone while driving.

Overall phones have changed society for the better and for the worse. Since their introduction, the cell phone has significantly changed how people talk and has increased the convenience of personal communication. But the life-changing benefits of the cell phone come with many controversial risks. The negative effects of deaths from distracted driving along with other health concerns cannot be overlooked. Many distracted cell phone driver accidents occur with young teenage drivers actively using their cellphones while operating a motor vehicle. While these events may make the evening news, they will never bring back the special life of that driver, the passengers or others that may have been hurt or killed. More private and government agencies need to further expose the dangerous links of driver cell phone use to human health. There is a great need to further educate the public of these risks. Having these agencies along with Hollywood, TV and social media, where images and messaging catch teens attention, could positively educate drivers and shape what safe cellphone usage looks like. This positive action may ultimately save lives.

Works Cited

"Cell phone ownership". Pew Research Today, 6 June 2013 pewresearch. org/fact-tank. Accessed 1 July 2019

"Cell Phone Safety". American Cancer Society, 4 April 2018 cancer. org/cancer/cancer-causes. Accessed 15 May 2019

"Cellular Phone Use and Texting While Driving Laws", 29 May 2019 ncsl. org/research/transportation/cellular. Accessed 24 June 2019

Creagan , Edward T. "Link between cell phones and cancer" 6 May 2018 mayoclinic. org/healthy-lifestyle. Accessed 15 May 2019

"Distracted Driving Laws", 1 June 2019 ghsa. org/state-laws/issues/Distracted. Accessed 24 June 2019

"Electromagnetic field and public health" 8 Oct. 2014 who. int/news-room/fact-sheets. Accessed 15 May 2019

"Mobile fact sheet". Pew Research Facts, 12 June 2019 pewinternet. org/fact-sheet/mobile. Accessed 1 July 2019

"Mobile Phones proven to save lives in emergencies", 11 July 2019 amta. org. au/articles/Mobile. phones. Accessed 24 June 2019

Weinlich, Michael. "Significant Acceleration of Response", 23 May 2018 journals. plos. org/plosone/article. Accessed 15 June 2019



## SCORE OF 4: An essay in this category demonstrates adequate mastery, although it will have lapses in quality. A typical essay develops a point of view on the issue and demonstrates competent critical thinking, using adequate examples, reasons, and other evidence to support its position; the essay is generally organized and focused, demonstrating some coherence and progression of ideas exhibits adequate; the essay may demonstrate inconsistent facility in the use of language, using generally appropriate vocabulary demonstrates some variety in sentence structure; the essay may have some errors in grammar, usage, and mechanics.

### Example essay with a score of 4:
Texting and Driving

Driving will always need your undivided attention at all times. There are many obvious reasons you shouldn't text and drive. You can get in a wreck, hit a pedestrian, and it puts your life at risk. Driving is a privilege and you should always follow the rules of the road. Using your mobile device can put you and the people around you in danger.

First of all, Texting and driving can get you in a terrible car wreck. When your on your phone your reaction time is bad. You can miss a stop sign and another car can come from the left or right side of you and you wouldn't see it coming. This can also raise your insurance rate up or you can be sued depending on how bad the accident is. Why risk it when you can wait or pull over to send that text? When you're looking down might not see pedestrians cross the street.

Besides getting into a car wreck you can also injure another person for being careless. Driving in a neighborhood needs your full attention. If you use your mobile device in a neighborhood you can either hit a pet, a jogger, or even a child if you're not paying attention. If such thing happens you can either get sued or go to jail for manslaughter. This is another major reason why you shouldn't be using your phone on the road.

Most importantly, getting distracted by your cell phone can put your life and other people's lives at risk. The most common deaths road deaths are caused by someone who were on their phones. You crashing can also cause a domino effect with other cars hitting each other on an intersection or a highway. That one text is not worth putting your life and other people's lives at risk. You don't want to end up in the hospital or even worse end up dead.

In conclusion, you should never use your phone while driving under no circumstances. If you need to make an emergency call, you should invest in a bluetooth hands free radio to make your phone calls. It is your duty to make the road you drive in safe for yourself and others. Make sure your eyes are always on the road no matter what.


## SCORE OF 3: An essay in this category demonstrates developing mastery, and is marked by ONE OR MORE of the following weaknesses: develops a point of view on the issue, demonstrating some critical thinking, but may do so inconsistently or use inadequate examples, reasons, or other evidence to support its position; the essay is limited in its organization or focus, or may demonstrate some lapses in coherence or progression of ideas displays; the essay may demonstrate facility in the use of language, but sometimes uses weak vocabulary or inappropriate word choice and/or lacks variety or demonstrates problems in sentence structure; the essay may contain an accumulation of errors in grammar, usage, and mechanics.

### Example essay with a score of 3:
Having a device near you while driving is very dangerous and a huge distraction. There are many consequences if you get caught driving with a cell phone. It distracts you from paying attention to your surroundings and you could hurt yourself or others around you. It is also against the law.

The U.S department of transportation reported that cell phones are involved in 1.6 million vehicle crashes each year. It has caused half a million injuries and around 6000 deaths annually. Texting while driving is even more dangerous than driving while under the influence of alcohol. People should put their devices down and focus on the roads and surrounding cars.

Everyday around 11 teens die in crashes caused by texting and driving. It only takes 3 seconds for a crash to occur after a driver becomes distracted by their cell phone or anything else. Holding a device while driving slows their reaction time by 49%. Car wrecks have killed nearly 32,999 people yearly and injuring around 2,239,000 people.

As of July 1,2018, in Georgia the "hands free law" was passed. The "hands free law" means that drivers will no longer be allowed to have a phone in their hand or supported by any part of their body. Texting while driving is highly illegal and it's good to see the state's law being put in to action.

We should not text and drive. It is overall a distraction and could lead you to death or you could kill an innocent person. The laws are very strict about texting and driving now. It's good to see the cops pushing the law so hard on people and if you don't listen then you suffer the consequences.


## SCORE OF 2: An essay in this category demonstrates little mastery, and is flawed by ONE OR MORE of the following weaknesses: develops a point of view on the issue that is vague or seriously limited, and demonstrates weak critical thinking, providing inappropriate or insufficient examples, reasons, or other evidence to support its position; the essay is poorly organized and/or focused, or demonstrates serious problems with coherence or progression of ideas; the essay displays very little facility in the use of language, using very limited vocabulary or incorrect word choice and/or demonstrates frequent problems in sentence structure; the essay contains errors in grammar, usage, and mechanics so serious that meaning is somewhat obscured.

### Example essay with a score of 2:
Drivers should not be able to be on the phone while driving because that causes accidents and while they are on there phone they are not looking at the rode. If your not looking at the rode how are you going to see what's going on you wouldn't be able to see what the cars are doing in front of you. If you are on the phone and you come across a stop sign you wouldn't be able to see and you keep going and you get hit by a car because you didn't have the right away that accident would be your fault because you were on your phone and you wasn't paying attention to the rode you could be on your phone at a red light and the light turns green and your still sitting there because your on your phone. Being on your phone can cause the police to pull you over and give you a big ticket price or worse take you to jail depending on what you did. The hole point is being on your phone while driving causes to many problems so the best thing to do is keep your phone in your pocket while you are driving. Because if you don't you will have a car accident research says that most car accidents that happen the people that caused the accident were on there phone your phone or text message can not be that important to the point were your risking your whole life.

## SCORE OF 1: An essay in this category demonstrates very little or no mastery, and is severely flawed by ONE OR MORE of the following weaknesses: develops no viable point of view on the issue, or provides little or no evidence to support its position; the essay is disorganized or unfocused, resulting in a disjointed or incoherent essay; the essay displays fundamental errors in vocabulary and/or demonstrates severe flaws in sentence structure; the essay contains pervasive errors in grammar, usage, or mechanics that persistently interfere with meaning.

### Example essay with a score of 1:
There have been an incredible amount of car accident caused by using cell phones while driving. There are about 421,000 people injured in 2017 by an accident caused by people that are described by people that are desecrated by looking at their phone. 1 out of 4 car accident is caused by texting and driving. So in response for the accident with a cellphone the government made new driving laws. In California there is now a law that states you cannot smoke and drive and also edibles even the passenger. Sometime people have different reaction time.

Because cannabis slows down your reaction is decreased by 21%.

Here are some helpful way to stay focus at all time when you driving. Try to talk to the person you see texting and driving to put down the phone while driving to ensure that every passenger is safe.14 % of people say they seen their parents on the phone. It has been studies to see who is more likely to get in an accident caused by texting. The studies have shown women are more likely to text and drive opposed to men drinking and driving. There are new apps for the phone that can stop all call and texts.

There are new laws that the government have made to put fear in people that like to use their mobile phone while driving.

So that people can stop creating a problem for drivers that use protective driving.

Craig hospital says '37 of the brain is distracted by a cellphone.


"""


def score_essay(
        essay: str,
        rubric: str = RUBRIC,
        ask_fn = ask_gpt,
        model: str = "gpt-4o",
        temperature: float = 0.5,
) -> Tuple[int, str]:
    """
    Return a holistic score (1-6) for `essay` under the provided `rubric`.
    Also returns GPT’s raw reply so you can inspect or store it.

    Parameters
    ----------
    essay : str
        Student draft.
    rubric : str
        Holistic rubric text that defines levels 1-6.
    ask_fn : callable(user, system, model, temperature) -> str
        Your standard chat wrapper.
    model, temperature : LLM parameters.

    Returns
    -------
    score : int
        Integer 1-6 extracted from GPT’s reply.
    raw_reply : str
        Full assistant message (useful if you later want explanations).
    """
    user_prompt = (
        "Below is a holistic rubric with levels 1-6, followed by a student essay.\n\n"
        "----- RUBRIC -----\n"
        f"{rubric}\n\n"
        "----- ESSAY -----\n"
        f"{essay}\n\n"
        "Please evaluate the essay strictly according to the rubric and output "
        "only the final integer score (1-6). Do not include any other text."
    )

    raw_reply = ask_fn(
        user=user_prompt,
        system=_GRADER_SYSTEM,
        model=model,
        temperature=temperature
    )

    # Extract the first integer 1-6
    match = re.search(r"\b([1-6])\b", raw_reply)
    if not match:
        raise ValueError(f"No 1-6 score found in GPT reply:\n{raw_reply}")
    return int(match.group(1)), raw_reply