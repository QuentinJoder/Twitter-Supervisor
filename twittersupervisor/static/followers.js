const api_prefix = '/api'

const vm = new Vue({
    el: '#app-content',
    delimiters: ['[[', ']]'],
    data: {
        followers: [],
        events: [],
        target_follower: null,
    },
    created() {
        this.getUsers()
    },
    methods: {
        // API calls
        getUsers: async function (){
            const response = await fetch(api_prefix + window.location.pathname);
            const object = await response.json();
            this.followers = object;
        },
        getEvents: async function (followerId){
            const response = await fetch(api_prefix + '/followers/' + followerId + '/events');
            const object = await response.json();
            this.events = object;
        },
        // Animation
        active: function (page) {
            if (page.localeCompare(window.location.pathname) ===  0) {
                return 'active';
            }
            return '';
        },
        collapsed: function (followerId) {
            if (followerId.localeCompare(this.target_follower) !== 0) {
                return 'collapsed'
            }
            return ''
        },
        show: function (followerId) {
            if (followerId.localeCompare(this.target_follower) === 0) {
                return 'show'
            }
            return ''
        },
        toggle: function(followerId) {
            if(followerId.localeCompare(this.target_follower) === 0) {
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
         // TODO: Decide what date format to use
        return value
    },
    follows: function (value) {
        if (value) {
            return "Follow";
        }
        return "Unfollow";
    }
    }
})