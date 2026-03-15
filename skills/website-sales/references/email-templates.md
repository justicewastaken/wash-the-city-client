# Email Templates

Customize these templates to match your voice and offer. Templates use placeholders in curly braces `{placeholder}`.

## Placeholders

- `{business_name}` - The business name (required)
- `{owner_name}` - Owner's name if known, otherwise "there"
- `{current_website}` - Current website URL (or "your current site")
- `{industry}` - Business industry/category
- `{portfolio_url}` - Your portfolio link
- `{your_phone}` - Your phone number
- `{setup_price}` - Your setup fee amount
- `{example_link}` - Example website you built for similar business

## Initial Outreach (Template: `initial`)

Best for first contact. Keeps it light, offers free portfolio work.

```
Subject: Quick question about {business_name}'s website

Hi {owner_name},

I was looking at {business_name}'s website {current_website} and noticed it could use a fresh look to better showcase what you do. As a student building my portfolio, I'd love to create you a brand new, modern website—completely free—to add to my portfolio.

If you like it, we can talk about a small setup fee (typically ${setup_price}) and optional monthly maintenance ($100/month) to keep it updated. No pressure—I just want to build something great for you and get real experience.

You can see some of my work here: {portfolio_url}

Would you be open to letting me take a shot at it?

Best,
Justice
{your_phone}
```

**Tips:**
- Keep it under 150 words
- Mention you specifically looked at their site (shows effort)
- "Student building portfolio" = lower pressure, social goodwill
- Include your phone for easy reply

## 3-Day Follow-up (Template: `followup-3d`)

Gentle nudge. Assume they're busy.

```
Subject: Following up: {business_name} website

Hi {owner_name},

Just wanted to follow up on my email about creating a new website for {business_name}. I'm still excited about the possibility of working with you and can have a draft ready within a week if you're interested.

Any thoughts?

Best,
Justice
```

## 7-Day Follow-up (Template: `followup-7d`)

Add social proof and urgency.

```
Subject: One more: {business_name} website idea

Hi {owner_name},

I know you're busy, but I wanted to share a quick example of a website I recently built for a similar {industry} business: {example_link}

If you'd like something like this for {business_name}, I'm offering a special rate this month. Let me know if you want to chat for 15 minutes.

Best,
Justice
```

## 14-Day Closing (Template: `followup-14d`)

Final attempt—polite exit.

```
Subject: Final: {business_name} website opportunity

Hi {owner_name},

This is my last email about the website offer. I want to make sure I'm not pushing too hard, but I genuinely believe I can create something that will help {business_name} attract more customers.

If you're interested, hit reply and we'll set up a quick call. If not, no worries at all—I appreciate your time either way.

All the best,
Justice
```

## Customization Tips

1. **Industry-specific hooks:**
   - Restaurant: "...help you showcase your menu and get more reservations"
   - Salon: "...let your beautiful work shine online and attract new clients"
   - Contractor: "...build trust with past project galleries and easy contact forms"

2. **Local connection:**
   - If targeting Eau Claire: "As a local Eau Claire student..."
   - If Minneapolis: "I'm based in the Twin Cities and love supporting local businesses"

3. **Portfolio quality:**
   - Build 2-3 stellar sample sites before outreach
   - Make them relevant to target industry if possible
   - Link directly to examples, not a generic homepage

4. **Response bait:**
   - End emails with easy YES questions: "Would you be open to...?"
   - Not: "Let me know if you're interested." (too passive)
   - Better: "Can I create a draft for you to review?"

---

**Need more templates?** Extend the `TEMPLATES` dict in `scripts/draft_outreach.py` following the same format.
