# Household & Retail Task Inventory for Teleoperated Chopstick Robot

**Created:** April 16, 2026

Sorted roughly by difficulty for a minimal chopstick-style gripper. Difficulty considers: precision needed, force needed, risk of damage, object variety, and environment complexity.

---

## Tier 1: Easy (pick up, move, put down)

### Floor / Surface Cleanup
- Pick up toys off the floor
- Pick up clothes off the floor and put in hamper
- Pick up shoes and place on rack
- Clear trash / wrappers off surfaces
- Pick up pet toys
- Collect remote controls, phones, loose items and return to designated spots
- Pick up books / magazines and shelve them
- Gather scattered pens, pencils, chargers

### Sorting
- Sort laundry into darks / lights / colors (pick up, drop in correct bin)
- Sort mail into piles
- Sort recycling vs trash
- Sort kids' toys into bins by type
- Sort silverware from dishwasher into drawer slots
- Sort screws, nails, small hardware into compartments

### Simple Transfers
- Move dishes from table to counter (near sink)
- Move grocery bags from door to counter
- Carry folded towels to closet shelf
- Move packages from doorstep inside
- Transfer items between shelves

---

## Tier 2: Medium (requires some positioning / orientation)

### Kitchen
- Load dishwasher (place cups, plates, bowls in slots)
- Unload dishwasher to counter
- Put groceries away (pantry items, canned goods, boxed goods)
- Wipe counter with a cloth (clamp cloth, drag)
- Take out trash bag (grip, lift, tie — hard)
- Set the table (place plates, cups, silverware)
- Clear the table after meals
- Move pots/pans to stove or cabinet
- Open/close cabinet doors (pull handle)
- Put food containers in fridge

### Bedroom
- Make bed — pull sheets and blankets up (drag, smooth)
- Fold laundry (t-shirts, towels, pants)
- Hang clothes on hangers and place in closet
- Organize dresser drawers
- Swap pillowcases
- Put away shoes in closet

### Bathroom
- Hang towels on rack
- Put toiletries back in cabinet
- Wipe counter with cloth
- Replace toilet paper roll
- Organize under-sink cabinet

### General
- Open/close doors (lever handles easier than round knobs)
- Open/close drawers
- Turn lights on/off (flip switch or press button)
- Water plants (carry small watering can, pour)
- Feed pets (scoop food, pour into bowl)
- Pick up and carry a broom or duster
- Dust surfaces (hold cloth, wipe)

---

## Tier 3: Hard (precision, force, or danger)

### Kitchen (precision)
- Crack eggs
- Stir pots
- Pour liquids (water, milk) into containers
- Chop vegetables (requires knife + cutting board + force)
- Open jars / bottles
- Measure ingredients
- Use microwave (press buttons, handle hot container)
- Operate blender / food processor buttons
- Peel fruit / vegetables
- Flip things in a pan

### Cleaning (force + coverage)
- Vacuum (push/pull heavy vacuum)
- Mop floor (push/pull mop, wring)
- Scrub dishes by hand
- Scrub bathtub / shower
- Clean windows
- Sweep floor

### Laundry (precision)
- Load washing machine (open door, stuff clothes in, add detergent, press buttons)
- Move wet clothes to dryer
- Iron clothes
- Fold fitted sheets
- Button/zip clothes before hanging

### Maintenance
- Change light bulbs
- Tighten loose screws
- Replace batteries in devices
- Unclog drain (use plunger)
- Patch small holes in wall

---

## Tier 4: Very Hard (multi-step, dangerous, or high dexterity)

### Cooking
- Full meal prep (sequence of chop, measure, combine, heat, stir, plate)
- Use oven (open heavy door, handle hot pans)
- Deep fry anything
- Bake (measure, mix, pour into molds, place in oven)
- Use sharp knives safely at speed

### Childcare Adjacent
- Prepare baby bottles
- Change diapers
- Bathe pets
- Assemble furniture
- Wrap gifts

### Repair
- Fix leaky faucet
- Patch drywall
- Paint a room
- Assemble IKEA furniture
- Sew / mend clothing

---

## Retail / Store Tasks

### Tier 1: Easy
- Stock shelves (pick item from box, place on shelf)
- Face shelves (pull products to front)
- Collect returned items and re-shelve
- Pick online orders (grab items, place in bag/bin)
- Sort incoming shipment boxes by department
- Collect shopping baskets and stack them
- Pick up trash / debris off floor
- Organize impulse buy displays near checkout
- Move small boxes from back room to floor

### Tier 2: Medium
- Price tagging (attach sticker to item)
- Build product displays (stack, arrange)
- Pack online orders into shipping boxes
- Scan items with handheld barcode scanner
- Organize clothing racks by size
- Fold clothes on display tables
- Hang clothes on racks
- Restock cooler / fridge shelves
- Wipe down shelves and displays
- Swap out sale signs / tags

### Tier 3: Hard
- Operate cash register / POS
- Handle fragile items (glass bottles, ceramics)
- Unload pallets
- Build elaborate store displays
- Assist customers (carry items, reach high shelves)
- Inventory counting with scanner
- Arrange flower displays
- Handle produce (soft fruits, vegetables without bruising)
- Clean up spills

---

## Best Starting Tasks (cheap chopstick robot, low risk, immediate value)

1. **Pick up stuff off the floor** — low precision, low damage risk, immediately useful, everyone hates doing it
2. **Sort laundry into bins** — grab and drop, no folding yet
3. **Clear table after meals** — repetitive, daily, annoying
4. **Stock shelves (retail)** — repetitive, high labor cost, structured environment
5. **Sort mail / packages** — simple pick and place
6. **Face shelves (retail)** — dead simple, huge labor sink in retail
7. **Collect toys** — parents would pay real money for this
8. **Put dishes on counter** — not into dishwasher yet, just table → counter

---

## Notes

- Tasks are rated for a teleoperated robot (human operator provides the intelligence)
- Difficulty is mostly about the gripper mechanics and damage risk, not the cognitive load (operator handles that)
- Folding laundry is medium difficulty — definitely achievable but not the starting point
- The biggest variable isn't the task, it's the object variety within each task
