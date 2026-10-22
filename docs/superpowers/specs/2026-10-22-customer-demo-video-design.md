# Customer demo video — storyboard and design

Status: DRAFT for Vishal's review (2026-10-22). Nothing has been captured yet.

## Goal

A narrated walkthrough video that a visitor can click to learn how to use the
Fresh & Quick website as a customer: where to sign up, what to fill in, what
happens after sign-up, and how to order, track and review. Web only, customer
journey only, about 5 minutes.

## Decisions (2026-10-22)

- Voice `en-IN-NeerjaNeural`; n8n paused (`docker stop n8n`) during capture and
  started again afterwards; only the scripts go into git (frames, build files
  and the MP4 are git-ignored).
- No admin information in the video (Vishal's rule): scene 10 is a text card,
  not the admin Registrations page.
- No dish in the database has option groups today, so scene 16 shows the "+"
  button adding straight to the basket and only mentions the options window.
- Chrome is maximised on a 2.25x display, so screenshots are 1568x675; each is
  scaled to 1920x826 above a 254 px caption panel.
- A password-manager extension draws icons inside inputs; `build.py` paints
  them out with the per-scene `masks` boxes.

## Deliverables

- `scripts/demo-video/out/Fresh_and_Quick_Demo.mp4` — 1920x1080, H.264 + AAC,
  captions burned in (git-ignored).
- `scripts/demo-video/out/Fresh_and_Quick_Demo.srt` — the same captions as a
  subtitle file.
- `scripts/demo-video/` — the storyboard as data (`storyboard.json`), the
  narration builder (edge-tts, voice `en-IN-NeerjaNeural` unless Vishal picks
  another) and the ffmpeg assembly script, so the video can be rebuilt with one
  command after a UI change.
- Screenshots live in `scripts/demo-video/frames/` (git-ignored or committed:
  Vishal's call; about 25 PNGs, a few MB).

## How it is made

1. Each scene is one or more full-page screenshots from a production build
   (`npx next build`, `npx next start -p 3000`), taken with Claude in Chrome at
   1920x1080.
2. Each scene's narration is synthesised with edge-tts; the audio length sets
   how long the scene is on screen (plus 0.6 s padding).
3. ffmpeg adds a slow zoom toward the scene's focus area, a highlight box
   around the field or button being described, the caption bar, and a 0.4 s
   crossfade between scenes. Title card at the start, closing card at the end.

## Safety rules during capture

- **No real email.** Sign-up (workflow 11), order accepted (03), delivered (05)
  and the review request (05) all send real Gmail when n8n runs. n8n is
  stopped with `docker stop n8n` (never `rm`) before capture and started again
  with `docker start n8n` afterwards. Needs Vishal's OK (see Open questions).
- **Dummy data only.** Customer "Priya Sharma", email
  `priya.demo@example.com`, phone `9876543210`, address at a real Mumbai
  landmark so sign-up geocoding passes (e.g. "Linking Road, Bandra West,
  Mumbai, Maharashtra 400050"). Mock card `4111 1111 1111 1111`, `12/30`.
- **Approval** is done through the admin portal (the admin route also lifts the
  sign-in ban; approving in SQL would not).
- **Order progress** without n8n: the order is moved through Accepted,
  Preparing, Ready and Partner assigned by the vendor portal / admin reassign,
  or by SQL on the throwaway order only, then the customer page plays the
  delivery animation, which marks it Delivered.
- **Clean-up** afterwards: delete the demo customer, its order, review and
  photo (same steps as "Reset Data" but limited to that one customer), and
  confirm nothing else changed.
- No real personal data appears on screen. The admin email and any real
  addresses are kept out of frame or masked.

## Storyboard

Times are estimates; the narration decides the real length.

| # | Screen | What is shown / done | Highlight | Narration |
|---|--------|----------------------|-----------|-----------|
| 1 | Title card | Logo text "Fresh & Quick", subtitle "How to use the website" | — | Welcome to Fresh and Quick. In the next few minutes we'll show you how to sign up, place your first order, track it to your door, and rate it. |
| 2 | Home, signed out | Hero "Fresh food, delivered fast.", carousels, left sidebar | Whole page | This is the home page. You can browse every restaurant and store without an account. The left menu lists the categories, like Restaurants, Grocery and Pet. |
| 3 | Home, sidebar bottom | "Sign In" and "Sign Up" buttons | Both buttons | To order, you need an account. New here? Click Sign Up. Already registered? Click Sign In. |
| 4 | Sign up form, empty | Card titled "Sign up" | Form | This is where you sign up. Every box tells you what goes in it. |
| 5 | Sign up, top fields filled | Full name, Email, Password | Those three fields | Enter your full name, your email address, and a password of at least six characters. |
| 6 | Sign up, contact and address filled | Phone, Address line 1 and 2, City, State, Pincode | Those fields | Next, your ten digit mobile number and your delivery address: address line one, an optional second line, city, state, and the six digit pincode. We check that the address is real, so please type it carefully. |
| 7 | Sign up, referral field | "Referral code (optional)" | That field | If a friend invited you, enter their referral code here. Otherwise leave it blank. Then click Sign up. |
| 8 | Pending popup | "Your registration approval is in progress…" | Popup | After you sign up, you'll see this message. Every new account is reviewed by our team. You'll get an email as soon as you're approved. |
| 9 | Log in, pending error | "Your registration is still awaiting admin approval." | Error text | If you try to log in before then, you'll see this reminder. Just wait for the approval email. |
| 10 | Text card (no admin screen: Vishal's rule, 2026-10-22, no admin information in the video) | "Our team reviews every new account" | — | Behind the scenes, our team reviews your details and approves your account. You'll get an email as soon as it's done. |
| 11 | Log in, filled | Email and password, "Log in" | Button | Once approved, come back to the log in page, enter your email and password, and click Log in. |
| 12 | Home, signed in | Header location pill shows the registered address; menu icon | Location pill | You're in. Your delivery address from sign-up is already set, at the top of the page. Stores are sorted by distance from you. |
| 13 | Location picker | "Choose delivery location" dialog, search box, map, "Save location" | Search box | To deliver somewhere else, click the location. Search for an address, drag the pin on the map, or use your current location, then click Save location. |
| 14 | Home, search and filters | Search box, filter chips, "♥ Favorites" | Search + chips | Search for a restaurant or a dish here, or narrow the list with filters like Rating or Under 30 minutes. Tap the heart on any store to save it to your Favorites. |
| 15 | Store page | Banner, rating, reviews, category pills | Category pills | This is a store's page. You'll see its rating and reviews from other customers, and the menu grouped by category. Click a category to jump to it. |
| 16 | Item customisation | Modal with "Required · choose 1", quantity, "Add 1 to cart" | Required group | Click the plus button to add a dish. If it has options, pick them here. Required choices must be made before you can add it. Choose the quantity, then click Add to cart. |
| 17 | Cart panel | "My Basket", line note, Order note, "Checkout" | Basket | Your basket appears on the right. Change quantities, add a note for a dish or for the whole order, like a gate code, then click Checkout. Your basket can hold items from one store at a time. |
| 18 | Checkout, contact | "Contact details": Name, Email, Phone | Section | At checkout, fill in who the order is for: name, email for order updates, and a mobile number. |
| 19 | Checkout, address | "Search for your address", "Use my pinned location", address fields | Section | Then the delivery address. Search for it, or click Use my pinned location to fill it in from your saved location. Check the pincode before you continue. |
| 20 | Checkout, promo and payment | Promo code + Apply, payment options | Section | Have a promo code? Enter it and click Apply. Then choose how to pay: card, UPI, or cash on delivery. Payments in this demo are simulated, so no real money is charged. |
| 21 | Place order | "Total to pay", "Place order" | Button | Check your total, and click Place order. |
| 22 | Order page, early status | 6-step timeline, status line, map | Timeline | Your order page shows every step: placed, accepted, preparing, ready, on the way and delivered. It updates by itself. |
| 23 | Order page, on the way | Map with partner, delivery animation dialog | Map + dialog | When a delivery partner picks up your order, you can follow them on the map, and a short animation shows your food on its way. |
| 24 | Order page, delivered | "Delivered", review form | Form | Once it's delivered, tell us how it went. Rate the store, optionally each dish and the delivery, add a comment or a photo, and click Submit review. |
| 25 | Your orders | List with "Reorder" | Reorder | All your past orders are under Orders. Click Reorder to put the same items back in your basket in one click. |
| 26 | Ask Zippy | Chat panel open with a question and answer | Bubble + panel | Need help at any time? Click Ask Zippy at the bottom right. Zippy can answer questions, find dishes, check your order, and even fill your basket for you. |
| 27 | Closing card | "Fresh & Quick — Fresh food, delivered fast." | — | That's it. Sign up, get approved, and enjoy your first order with Fresh and Quick. |

Estimated length: about 5 minutes.

## Out of scope

- Vendor, delivery-partner and admin portal walkthroughs (only the one admin
  approval shot in scene 10).
- The phone app.
- A "Watch demo" button on the website (a separate feature if wanted).
- Background music.

## Open questions for Vishal

1. OK to `docker stop n8n` during capture and `docker start n8n` afterwards?
   (It keeps the container and all workflows; it only pauses them.)
2. Voice: Neerja (female) or Prabhat (male)? Samples in the scratchpad.
3. Commit the screenshots in `scripts/demo-video/frames/`, or keep them
   git-ignored and commit only the scripts and the final MP4?
4. Is the MP4 size fine in git (expected 30 to 60 MB), or should it live
   outside the repo?
