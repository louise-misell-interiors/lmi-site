const apiUrl = "/graphql/";

export class GraphQLError extends Error {
    constructor(result, ...args) {
        super(...args);
        this.result = result;
    }
}

export const fetchGQL = (query, variables) =>
    fetch(apiUrl, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify({query: query, variables: variables}),
    })
        .then(res => {
            if (!res.ok) {
                console.error(res);
                throw new GraphQLError(res);
            }
            return res;
        })
        .then(res => res.json())
        .then(res => {
            if (res.errors) {
                console.error(res);
                throw new GraphQLError(res);
            }
            return res
        });