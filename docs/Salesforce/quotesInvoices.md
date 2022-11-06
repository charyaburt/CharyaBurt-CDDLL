---
layout: page
title: Creating Quotes and Invoices
parent: Salesforce
---

# Quotes and Invoices

* While the Finance department handles accounting, bookkeeping, and sometimes payments, it is on us to negotiate with the client on services fees. We first create a quote in Salesforce for the client only, then generate an invoice for Finance to process. We are also responsible for locking in the initial deposit (either 100% or 50% of the quoted amount).

## Quotes

* Quotes are only for the the client and for Preservation's internal moves management. Quotes are usually generated during the "Negotiation" stage of an Opportunity. We generally do not alert the Finance department of income while a project is in this phase; the money is not guaranteed.

## Invoices

* Invoices are for the the client and the Finance department. Note, the invoicing functionality is constantly evolving. Please update this page if you notice missing, added, or replaced steps in the process, or if you encounter new terminology.
    - In the Quotes, choose "Create PDF" then from the dropdown menu chose "EMAIL 50" template. (This method only works if you have created a quote with line items first)
    - Look over the PDF and make sure it is correct. Choose "Save and Send and Email"
    - At the bottom of email page, close "Select Template."
    - Choose "QUOTE INVOICE" and the invoice payment template should appear. Please test the link and make sure it is working. (The Quote/Invoice number needs to be in the body of the email in order for Finance to process the email accordingly)
    - Change the Related To field to "Opportunity"
    - Add the contacts name in the To field
    - In the CC field, type innesa@bavc.org
    - In the BCC field, type preservation@bavc.org
    - Edit the Subject Line, Text, and Email fields as you see fit.  (this invoice will be sent from your email address).
    - You might have to email the client in your other correspondence that you have sent an invoice and that they should check their spam folder if they haven't received it (this happens sometimes when sending emails through Salesforce).
