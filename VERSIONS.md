08.27.24.req
- Journal functionality
- Track progress
    - Establish identity for the session
    - Show graphs
        - bell-curve position
        - score on a quadrant
        - journal - score relationship
    - Load assessment from the previous session
- Explain relationship between Number of lives to Moksha and Assessment categories

08.28.24.rel
- Track progress
    - Establish identity for the session

08.29.24.rel
- Journal functionality
- Track progress
    - Show graphs
        - journal - score relationship

03.09.25.rel
Sample APIs
curl -c cookies.txt -d '{"email":"sdixit@ohioedge.com"}' -X POST localhost:8503/get-token -H "Content-Type: application/json"
curl -b cookies.txt localhost:8503/validate-token/bbf8fb01 -H "Content-Type: application/json"
curl -b cookies.txt localhost:8503/session-info -H "Content-Type: application/json"
curl -b cookies.txt localhost:8503/assessment-questionnaire -H "Content-Type: application/json"
curl -b cookies.txt localhost:8503/assessment-answers/latest -H "Content-Type: application/json"