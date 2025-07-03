# schedule_maker
picking courses is lame. too much time. get AI to do it. YAY!

#learnings
1) Batch everything. Test everything. For uploading elements to a DB or scraping something, test first, do it in small batches. maybe even build the entire workflow with the smaller data before scaling it up. This lets you see the different points of failure and how you can improve it. for example, scraping, it woulda been really helpful to scrape not just the course names, but also the course ID/#, i.e BEPP 1000. only realized this later.
2) I haven't done it here. but building evals would prolly be pretty helpful. 

KEY TAKEAWAY (!!!!!!): 
make sure it works LMAO. don't just dive into building. figure out what is needed to get it to a certain level of accuracy. what is the necessary context. do this manually. THEN backfill to the necessary workflow and tool use. 
