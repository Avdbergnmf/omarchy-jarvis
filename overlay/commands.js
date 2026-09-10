// Single UI command registry. Extend here when adding a deterministic command.
globalThis.JarvisCommands = [
 {name:'/report', usage:'/report ', description:'Report a problem with a run'},
 {name:'/feature', usage:'/feature ', description:'Suggest a feature'},
 {name:'/backlog', usage:'/backlog ', description:'List open bugs and features'},
 {name:'/dispatch', usage:'/dispatch ', description:'Prepare a handoff: <issue> to <agent>'},
 {name:'/train', usage:'/train ', description:'Open Training mode'},
];
