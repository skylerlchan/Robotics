"""Catalog of tasks people expect robots to do. Each line: domain | task | skills | objects | needs | source | demo-slug.
needs: rigid = doable with rigid-body physics now; deform = cloth, paper, bags, food; fluid = liquids or granular; mobile = needs a moving base;
tools = holds and operates a tool; precision = sub-5 mm alignment; people = physical contact with a person; heavy = over 5 kg."""
import json, os
SRC = {"B1K": ("BEHAVIOR-1K survey, 1,461 respondents ranking 2,090 activities", "https://arxiv.org/abs/2403.09227"),
       "RC365": ("RoboCasa365, ten foundational skills, 65 atomic and 365 tasks", "https://arxiv.org/abs/2603.04356"),
       "OXE": ("Open X-Embodiment, 22 robots, 527 skills; pick-place, push, open, close dominate", "https://arxiv.org/abs/2310.08864"),
       "SHAP": ("Southampton Hand Assessment Procedure, 26 timed tasks", "https://shap.ecs.soton.ac.uk/about.php"),
       "JT": ("Jebsen-Taylor Hand Function Test, 7 subtests", "https://oml.eular.org"),
       "ARAT": ("Action Research Arm Test, 19 items", "https://www.physio-pedia.com"),
       "ADL": ("Mitzner et al. 2013, older adults' openness to robot help with daily living tasks", "https://pmc.ncbi.nlm.nih.gov"),
       "YOO": ("Yoo et al. 2024, preferences and expectations for home robot tasks", "https://pubmed.ncbi.nlm.nih.gov"),
       "IND": ("Automate.org and RoboDK industrial pick-and-place task lists", "https://www.automate.org"),
       "HUM": ("Tasks shown or promised by 1X NEO, Tesla Optimus and Figure", "https://www.1x.tech/discover/neo-home-robot"),
       "RLB": ("RLBench, 100 tabletop tasks", "https://sites.google.com/view/rlbench"),
       "LIB": ("LIBERO, 130 language-conditioned tasks", "https://libero-project.github.io")}
ROWS = """
Kitchen | Load the dishwasher with plates and cups | pick-place, insertion, open door | plates, cups, rack | rigid | B1K, RC365 |
Kitchen | Unload the dishwasher and put dishes in cabinets | pick-place, open door, mobile | plates, cabinet | rigid, mobile | B1K, RC365 |
Kitchen | Wash dishes by hand | tools, fluid | sponge, sink, dishes | fluid, tools | B1K |
Kitchen | Wipe the counter with a cloth | tools | cloth, counter | deform, tools | B1K, HUM |
Kitchen | Clear the table after a meal | pick-place, mobile | plates, cutlery | rigid, mobile | B1K, HUM |
Kitchen | Set the table | pick-place, mobile | plates, glasses, cutlery | rigid, mobile | B1K |
Kitchen | Pour a glass of water from a jug | pour | jug, glass | fluid | SHAP, RC365 |
Kitchen | Pour milk from a carton | pour | carton, bowl | fluid, deform | SHAP |
Kitchen | Make coffee with a pod machine | press button, insertion, open lid | machine, pod, cup | rigid, fluid | RC365 |
Kitchen | Fill and switch on a kettle | fluid, press | kettle, tap | fluid | RC365 |
Kitchen | Open the fridge and take out a bottle | open door, pick-place | fridge, bottle | rigid | RC365, OXE | bottle
Kitchen | Put groceries away in the fridge | open door, pick-place, mobile | bags, packages | rigid, mobile | B1K, RC365 |
Kitchen | Restock a pantry shelf | pick-place | cans, boxes | rigid | RC365, HUM |
Kitchen | Chop vegetables with a knife | tools, cutting | knife, board, vegetables | tools, deform | B1K, SHAP |
Kitchen | Peel a potato | tools | peeler, potato | tools, deform | B1K |
Kitchen | Stir a pot on the stove | tools | spoon, pot | tools, fluid | B1K |
Kitchen | Flip a pancake with a spatula | tools | spatula, pan | tools, deform | HUM |
Kitchen | Crack an egg into a bowl | precision | egg, bowl | deform, precision | B1K |
Kitchen | Unscrew a jar lid | twist, grasp | jar | rigid | SHAP, RC365 | knob
Kitchen | Unscrew a bottle cap | twist | bottle | rigid, precision | SHAP |
Kitchen | Open a can with an opener | tools, twist | opener, can | tools | B1K |
Kitchen | Slice bread | tools | knife, loaf | tools, deform | B1K |
Kitchen | Spread butter on toast | tools | knife, toast | tools, deform | B1K |
Kitchen | Heat a meal in the microwave | open door, pick-place, press, close door | microwave, plate | rigid | RC365 | button
Kitchen | Turn a stove knob | twist knob | knob | rigid | RC365 | knob
Kitchen | Turn a tap lever on and off | lever | tap | rigid | RC365 |
Kitchen | Open and close the oven door | door | oven | rigid | RC365 |
Kitchen | Slide an oven rack out and in | sliding rack | rack | rigid | RC365 |
Kitchen | Lift a pot lid and put it back | lid, pick-place | lid, pot | rigid | RC365 |
Kitchen | Insert a plate into a dish rack | insertion | plate, rack | rigid, precision | RC365 |
Kitchen | Hang a mug on a hook | precision hang | mug, hook | rigid, precision | LIB |
Kitchen | Take a hot tray out of the oven | pick-place, heavy | tray, mitt | rigid, heavy | B1K |
Kitchen | Season a dish with a shaker | shake | shaker | fluid | RC365 |
Kitchen | Serve food from a pot onto plates | tools | ladle, pot, plates | tools, fluid | B1K |
Kitchen | Throw packaging into the bin | pick-place, open lid, mobile | packaging, bin | rigid, mobile | B1K, RC365 |
Kitchen | Take out the trash bag | grasp, heavy, mobile | bag | deform, heavy, mobile | B1K, YOO |
Kitchen | Fit a new trash bag | deform | bag, bin | deform | B1K |
Cleaning | Scrub the bathroom floor | tools | brush, floor | tools, fluid, mobile | B1K |
Cleaning | Mop the kitchen floor | tools, mobile | mop, bucket | tools, fluid, mobile | B1K, YOO |
Cleaning | Clean the bathtub | tools | sponge, tub | tools, fluid | B1K |
Cleaning | Clean the toilet | tools | brush | tools, fluid | B1K |
Cleaning | Vacuum a carpet | tools, mobile | vacuum | tools, mobile | B1K, HUM |
Cleaning | Sweep with a broom and dustpan | tools, mobile | broom, dustpan | tools, fluid, mobile | B1K, HUM |
Cleaning | Dust the shelves | tools, mobile | duster | tools, mobile | B1K |
Cleaning | Wipe a dining table | tools | cloth | deform, tools | B1K, OXE |
Cleaning | Clean windows and mirrors | tools | squeegee, spray | tools, fluid | B1K |
Cleaning | Wipe the stovetop | tools | cloth | deform, tools | B1K |
Cleaning | Scrub pots and pans | tools | scourer, pan | tools, fluid | B1K |
Cleaning | Empty the vacuum cleaner bin | pour | bin | fluid | B1K |
Cleaning | Pick up litter from the floor | pick-place, mobile | litter, bin | rigid, mobile | B1K, HUM |
Cleaning | Wipe up a spill | tools | cloth | deform, fluid | B1K |
Cleaning | Clean the sink | tools | sponge | tools, fluid | B1K |
Cleaning | Change the bed sheets | deform | sheets | deform | B1K, HUM |
Cleaning | Make the bed | deform | duvet, pillows | deform | B1K, HUM |
Cleaning | Put toys back in a box | pick-place, mobile | toys, box | rigid, mobile | B1K, HUM | box
Cleaning | Water houseplants | pour, mobile | watering can | fluid, mobile | B1K, YOO |
Cleaning | Clean a litter box | tools | scoop | fluid, tools | B1K |
Laundry | Sort laundry by colour | deform, pick-place | clothes | deform | B1K |
Laundry | Load the washing machine | deform, open door | clothes, machine | deform | B1K, YOO |
Laundry | Move wet laundry to the dryer | deform | clothes | deform | B1K |
Laundry | Unload the dryer into a basket | deform | clothes, basket | deform | B1K |
Laundry | Fold a T-shirt | deform | T-shirt | deform | B1K, HUM |
Laundry | Fold towels | deform | towels | deform | B1K, HUM |
Laundry | Pair socks | deform | socks | deform | B1K |
Laundry | Put a shirt on a hanger | deform, precision | shirt, hanger | deform, precision | B1K |
Laundry | Hang laundry on a line with pegs | deform, precision, mobile | pegs, line | deform, precision, mobile | B1K |
Laundry | Iron a shirt | tools, deform | iron, shirt | tools, deform | B1K |
Laundry | Put folded clothes in a drawer | deform, open drawer | clothes, drawer | deform | B1K, HUM | drawer
Laundry | Zip a jacket | deform, precision | zip | deform, precision | SHAP |
Laundry | Button a shirt | deform, precision | buttons | deform, precision | SHAP |
Laundry | Tie shoelaces | deform, precision, bimanual | laces | deform, precision | B1K |
Laundry | Help someone put on a jacket | deform, people | jacket | deform, people | ADL |
Tidying | Put books back on a shelf | pick-place, insertion | books, shelf | rigid | B1K, HUM | box
Tidying | Organise a shelf by size | pick-place | boxes, jars | rigid | HUM | stack
Tidying | Put shoes on the rack | pick-place, mobile | shoes | rigid, mobile | B1K |
Tidying | Hang a coat on a hook | deform | coat | deform | B1K |
Tidying | Put remotes and cables in a drawer | pick-place, open drawer | remote, drawer | rigid | B1K | drawer
Tidying | Sort the mail | deform | envelopes | deform | B1K |
Tidying | Collect cups left around the house | mobile, pick-place | cups | rigid, mobile | B1K, HUM | cup
Tidying | Put things back where they belong | mobile, pick-place | many | rigid, mobile | B1K |
Tidying | Stack chairs | heavy, bimanual | chairs | rigid, heavy | B1K |
Tidying | Pack a suitcase | deform | clothes, suitcase | deform | B1K |
Tidying | Wrap a gift | deform, precision | paper, tape | deform, precision | B1K |
Tidying | Assemble flat-pack furniture | tools, precision, bimanual | panels, screws | tools, precision | B1K |
Tidying | Hang a picture frame | precision, tools | frame, nail | precision, tools | B1K |
Tidying | Change a light bulb | twist, precision | bulb | rigid, precision | B1K | knob
Tidying | Replace batteries in a remote | precision, insertion | batteries | rigid, precision | B1K |
Tidying | Plug in a charger | insertion, precision | plug, socket | rigid, precision | RC365 |
Care | Pick up something dropped on the floor | pick-place, mobile | any small object | rigid, mobile | ADL, YOO | cube25
Care | Bring a glass of water to a person | carry, mobile, handover | glass | fluid, mobile, people | ADL |
Care | Hand an object to a person | handover, people | any | rigid, people | ADL, OXE |
Care | Open a child-proof medicine bottle | twist, push, precision | bottle | rigid, precision | ADL |
Care | Sort pills into a weekly organiser | precision, small objects | pills, organiser | rigid, precision | ADL |
Care | Feed someone with a spoon | tools, people | spoon, bowl | tools, fluid, people | ADL |
Care | Hold a cup with a straw for someone | hold, people | cup | fluid, people | ADL |
Care | Brush someone's hair | tools, people | brush | tools, people | ADL |
Care | Apply lotion to an arm | people | lotion | fluid, people | ADL |
Care | Help put on socks | deform, people | socks | deform, people | ADL |
Care | Help someone from bed to a chair | people, heavy | none | people, heavy | ADL |
Care | Reposition someone in bed | people, heavy | none | people, heavy | ADL |
Care | Push a wheelchair | mobile, people | wheelchair | mobile, people | ADL |
Care | Carry groceries in from the car | heavy, mobile | bags | deform, heavy, mobile | ADL, YOO |
Care | Fetch an item from a high shelf | reach, mobile | any | rigid, mobile | ADL, YOO | cup
Care | Open a door for someone | door, mobile | door | rigid, mobile | ADL |
Care | Turn the pages of a book | deform, precision | book | deform, precision | SHAP, ADL |
Care | Hold a tablet at reading height | hold | tablet | rigid | ADL |
Care | Write or sign with a pen | tools, precision | pen | tools, precision | JT |
Care | Unlock a door with a key | precision, twist | key | rigid, precision | SHAP |
Care | Press an elevator button | press | button | rigid | ADL | button
Office | Restock shelves in a store | pick-place, mobile | products | rigid, mobile | HUM, IND | heavy
Office | Scan and bag groceries at a till | pick-place, deform | products, bags | deform | IND |
Office | Count inventory by picking and scanning | pick | products | rigid | IND |
Office | Carry drinks on a tray | carry | tray, glasses | fluid | B1K, SHAP |
Office | Bus tables in a restaurant | pick-place, mobile | dishes | rigid, mobile | B1K |
Office | Make a hotel bed | deform | sheets | deform | B1K |
Office | Deliver an item from room to room | mobile, handover | any | rigid, mobile | HUM |
Office | Sort parcels by label | pick-place | parcels | rigid | IND |
Office | File papers in a folder | deform | paper | deform | B1K |
Office | Refill a printer paper tray | deform stack | paper | deform | B1K |
Office | Open and close window blinds | pull cord | cord | deform | B1K |
Office | Water the office plants | pour, mobile | can | fluid, mobile | B1K |
Warehouse | Pick mixed items from a bin | pick | mixed SKUs | rigid | IND, OXE | ball
Warehouse | Pick items into a tote | pick-place | items, tote | rigid | IND |
Warehouse | Lift and move a full tote | heavy, bimanual | tote | rigid, heavy | HUM, IND |
Warehouse | Depalletize boxes | heavy, stacking | boxes | rigid, heavy | IND |
Warehouse | Palletize boxes | stacking, heavy | boxes | rigid, heavy | IND | stack
Warehouse | Unload a truck | heavy, mobile | boxes | rigid, heavy, mobile | IND |
Warehouse | Pack items into a shipping box | pick-place, insertion | items, box | rigid | IND |
Warehouse | Seal a box with tape | deform, tools | tape | deform, tools | IND |
Warehouse | Sort parcels onto conveyors | pick-place | parcels | rigid | IND |
Warehouse | Apply a shipping label | deform | label | deform, precision | IND |
Warehouse | Handle sacks and bags | deform, heavy | sacks | deform, heavy | IND |
Warehouse | Pick from a shelf onto a cart | mobile, pick | products | rigid, mobile | IND |
Manufacturing | Load and unload a CNC machine | pick-place, door, precision | parts, fixture | rigid, precision | IND |
Manufacturing | Peg-in-hole insertion | insertion, precision | peg, hole | rigid, precision | RLB, RC365 |
Manufacturing | Drive a screw with a screwdriver | tools, twist | screwdriver, screw | tools, precision | SHAP, IND |
Manufacturing | Thread a nut onto a bolt | twist, bimanual | nut, bolt | rigid, precision | ARAT, IND |
Manufacturing | Route a cable through clips | deform | cable, clips | deform, precision | IND |
Manufacturing | Insert a connector | insertion, precision | connector | rigid, precision | IND |
Manufacturing | Kit parts into a tray | pick-place | parts, tray | rigid | IND |
Manufacturing | Snap-fit two parts together | insertion, force | parts | rigid, precision | IND |
Manufacturing | Press-fit a bearing | precision, force | bearing | rigid, precision, heavy | IND |
Manufacturing | Handle sheet metal blanks | heavy, flat | sheets | rigid, heavy | IND |
Manufacturing | Deburr and sand an edge | tools, force control | sander | tools | IND |
Manufacturing | Inspect a part by rotating it in hand | in-hand rotation | part | rigid | IND |
Manufacturing | Tighten a bolt with a wrench | tools, twist | wrench | tools | IND |
Manufacturing | Insert a battery module into a pack | heavy, precision | module | rigid, heavy, precision | HUM, IND |
Manufacturing | Pick a part from a moving conveyor | dynamic pick | parts | rigid | IND |
Lab | Cap and uncap sample vials | twist, precision | vials | rigid, precision | IND | knob
Lab | Pipette liquid between tubes | tools, precision | pipette | tools, fluid, precision | IND |
Lab | Load tubes into a centrifuge | insertion, lid | tubes, rotor | rigid, precision | IND |
Lab | Handle petri dishes | flat pick, precision | dishes | rigid, precision | IND |
Lab | Open sterile packaging | deform | packaging | deform | IND |
Lab | Hand instruments to a surgeon | handover, people | instruments | rigid, people | ADL |
Lab | Restock a medical cart | pick-place, mobile | supplies | rigid, mobile | IND |
Lab | Disinfect a surface | tools | wipe | deform, fluid, tools | IND |
Outdoor | Harvest apples from a tree | delicate pick, mobile | apples | deform, mobile | IND |
Outdoor | Pick strawberries | delicate pick, precision | berries | deform, precision | IND |
Outdoor | Pull weeds | deform, mobile | weeds | deform, mobile | B1K |
Outdoor | Water the garden with a hose | fluid, deform | hose | fluid, deform | B1K |
Outdoor | Mow the lawn | tools, mobile | mower | tools, mobile | B1K, YOO |
Outdoor | Rake leaves | tools, mobile | rake | tools, fluid, mobile | B1K |
Outdoor | Shovel snow | tools, heavy, mobile | shovel | tools, heavy, mobile | B1K |
Outdoor | Plug in an electric car | insertion, heavy | charger | rigid, precision, heavy | HUM |
Outdoor | Wash a car | tools, fluid | sponge, hose | tools, fluid | B1K |
Outdoor | Change a car tyre | tools, heavy, precision | jack, wrench | tools, heavy, precision | B1K |
Outdoor | Carry firewood | heavy, mobile | logs | rigid, heavy, mobile | B1K |
Outdoor | Fill a pet's food bowl | pour | kibble, bowl | fluid | B1K, YOO |
Clinical | SHAP abstract: spherical grip, light and heavy | grasp | sphere | rigid | SHAP | ball
Clinical | SHAP abstract: tripod grip, light and heavy | grasp | small cylinder | rigid | SHAP | bottle
Clinical | SHAP abstract: power grip, light and heavy | grasp | large cylinder | rigid | SHAP | heavy
Clinical | SHAP abstract: lateral grip, light and heavy | pinch | card | rigid, precision | SHAP |
Clinical | SHAP abstract: tip pinch, light and heavy | pinch | small cube | rigid, precision | SHAP | cube25
Clinical | SHAP abstract: extension grip, light and heavy | grasp | plate | rigid | SHAP | box
Clinical | SHAP: pick up coins into a slot | pinch, precision | coins | rigid, precision | SHAP |
Clinical | SHAP: button board | deform, precision | buttons | deform, precision | SHAP |
Clinical | SHAP: simulated food cutting | tools | knife, putty | tools, deform | SHAP |
Clinical | SHAP: page turning | deform | page | deform, precision | SHAP |
Clinical | SHAP: jar lid | twist | jar | rigid | SHAP | knob
Clinical | SHAP: glass jug pouring | pour | jug | fluid | SHAP |
Clinical | SHAP: carton pouring | pour | carton | fluid, deform | SHAP |
Clinical | SHAP: lift a heavy object | grasp, lift | tin | rigid | SHAP | heavy
Clinical | SHAP: lift a light object | grasp, lift | tin | rigid | SHAP | cup
Clinical | SHAP: lift a tray | bimanual carry | tray | rigid | SHAP |
Clinical | SHAP: rotate a key | precision, twist | key | rigid, precision | SHAP |
Clinical | SHAP: open and close a zip | deform, precision | zip | deform, precision | SHAP |
Clinical | SHAP: rotate a screw | tools, twist | screwdriver | tools, precision | SHAP |
Clinical | SHAP: door handle | lever | handle | rigid | SHAP |
Clinical | Jebsen: writing a sentence | tools, precision | pen | tools, precision | JT |
Clinical | Jebsen: turning over cards | deform, precision | cards | deform, precision | JT |
Clinical | Jebsen: small common objects into a can | pinch, place | paperclip, coin, cap | rigid, precision | JT | box
Clinical | Jebsen: simulated feeding | tools | spoon, beans | tools, fluid | JT |
Clinical | Jebsen: stacking checkers | stack, precision | checkers | rigid, precision | JT | stack
Clinical | Jebsen: large light cans | grasp | cans | rigid | JT | cup
Clinical | Jebsen: large heavy cans | grasp | cans | rigid | JT | heavy
Clinical | ARAT grasp: 10 cm block | grasp, lift | block | rigid | ARAT |
Clinical | ARAT grasp: 2.5 cm block | grasp, lift | block | rigid, precision | ARAT | cube25
Clinical | ARAT grasp: 5 cm block | grasp, lift | block | rigid | ARAT | stack
Clinical | ARAT grasp: 7.5 cm block | grasp, lift | block | rigid | ARAT |
Clinical | ARAT grasp: cricket ball | grasp, lift | ball | rigid | ARAT | ball
Clinical | ARAT grasp: sharpening stone | grasp, lift | stone | rigid | ARAT | box
Clinical | ARAT grip: pour water glass to glass | pour | glasses | fluid | ARAT |
Clinical | ARAT grip: 2.25 cm tube | grasp, place | tube | rigid | ARAT | bottle
Clinical | ARAT grip: 1 cm tube | grasp, place | tube | rigid, precision | ARAT |
Clinical | ARAT grip: washer over a bolt | precision place | washer, bolt | rigid, precision | ARAT |
Clinical | ARAT pinch: 6 mm ball bearing, six variants | pinch | bearing | rigid, precision | ARAT |
Clinical | ARAT pinch: marble, six variants | pinch | marble | rigid, precision | ARAT |
Clinical | ARAT gross: hand behind head, on head, to mouth | arm motion | none | rigid | ARAT |
Beyond | Cage an object without touching it | cage | any | rigid | this design |
Beyond | Move many objects at once | parallel | many | rigid | this design |
Beyond | Reach through an 8 mm hole | thin reach | box with hole | rigid | this design |
Beyond | Do three jobs at once with one effector | split | parts | rigid | this design |
Beyond | Lift a load by wrapping it | wrap | bottle, bar | rigid | this design |
Beyond | Keep working after losing three tendrils | redundancy | any | rigid | this design |
Beyond | Catch a dropped object | dynamic cage | ball | rigid | this design |
Beyond | Hold a shape indefinitely at zero power | jam | any | rigid | this design |
"""
BENCH = {"hold": "Hold a shape indefinitely at zero power", "cage": "Cage an object without touching it", "parallel": "Move many objects at once", "ring": "Reach through an 8 mm hole", "wrap": "Lift a load by wrapping it"}
def load():
    rows = []
    for i, line in enumerate(l for l in ROWS.strip().splitlines() if l.strip()):
        p = [x.strip() for x in line.split("|")]
        domain, task, skills, objects, needs, src = p[:6]; demo = p[6] if len(p) > 6 and p[6] else ""
        needs = [n.strip() for n in needs.split(",")]
        status = "demo" if demo else ("bench" if task in BENCH.values() else ("ready" if needs == ["rigid"] or set(needs) <= {"rigid", "precision", "heavy"} else "later"))
        gate = "rigid physics" if status != "later" else ("deformables" if "deform" in needs else "fluids" if "fluid" in needs else "mobile base" if "mobile" in needs else "tool use" if "tools" in needs else "human contact" if "people" in needs else "rigid physics")
        rows.append(dict(id=i+1, domain=domain, task=task, skills=[s.strip() for s in skills.split(",")], objects=objects, needs=needs, sources=[s.strip() for s in src.split(",")], demo=demo, status=status, gate=gate))
    return rows
if __name__ == "__main__":
    rows = load(); here = os.path.dirname(os.path.abspath(__file__))
    json.dump(dict(sources=SRC, tasks=rows), open(os.path.join(here, "tasks.json"), "w"), indent=1)
    from collections import Counter
    print(len(rows), "tasks;", Counter(r["status"] for r in rows), Counter(r["domain"] for r in rows))
