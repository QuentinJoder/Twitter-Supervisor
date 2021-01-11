const api_prefix = '/api'

const vm = new Vue({
    el: '#twitter-supervisor',
    delimiters: ['[[', ']]'],
    data: {
        followers: [],
        events: [],
        target_follower: null,
    },
    created() {
        this.getFollowers()
    },
    methods: {
        getFollowers: async function (){
            const response = await fetch(api_prefix + '/followers');
            const object = await response.json();
            console.log(object)
            this.followers = object;
        },
        getEvents: async function (followerId){
            const response = await fetch(api_prefix + '/followers/' + followerId + '/events');
            const object = await response.json();
            console.log(object)
            this.events = object;
        },
        collapsed: function (followerId) {
            if (followerId !== this.target_follower) {
                return 'collapsed'
            }
            return ''
        },
        show: function (followerId) {
            if (followerId === this.target_follower) {
                return 'show'
            }
            return ''
        },
        toggle: function(followerId) {
            if(this.target_follower === followerId) {
                this.target_follower = null
                this.events = []
            } else {
                this.target_follower = followerId
                this.getEvents(followerId)
            }
        }
    },
    filters: {
    date: function (value) {
        date = new Date(value);
        formattedDate = date.getDate() < 10 ? '0': ''
        formattedDate += date.getDate()
        formattedDate += date.getMonth() < 9 ? '-0': '-'
        formattedDate += (date.getMonth() + 1)
        return formattedDate + '-' + date.getFullYear();
    },
    follows: function (value) {
        if (value === 1) {
            return "Follow";
        }
        return "Unfollow";
    }
    }
})