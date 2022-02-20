# myntra-lowest-price-tracker
A telegram bot that keeps a track of the lowest prices of any product on Myntra

<h3>I reverse engineered Myntra's (eCommerce website) private API. I'm here to discuss a small project done by me Please note that: I do not leak any private information and I'm sharing it for educational purposes, do not claim any responsibility or legality.</h3>

<b>This bot does a few things:</b> scrape all publicly available data of a specific product and let users know if the price changes, users can also check Highest, Lowest, and Average prices


<h2>How am I fetching product prices and other publicly available data?</h2>

<ul>
  <li>Once the user will send a direct product link, the bot will fetch all publicly available data from Myntra.</li>
  <li>When the user verifies if this is a valid product, all publicly available data of this project will be saved in the DB.</li>
  <li>Every 1 hour, the bot will look for any updates ( publicly available data) of all saved products, and if the price changes, the bot will notify the user.</li>
  <li>Users can also check what was the highest, lowest, and average price  ( all this is possible because I'm saving all products when any user checks for a specific product through the bot.</li>
  <li>Users can also download well-structured JSON data of any specific product that is saved in DB.</li>
</ul>


Very simple project but helpful, because everyone likes to spend less. 

