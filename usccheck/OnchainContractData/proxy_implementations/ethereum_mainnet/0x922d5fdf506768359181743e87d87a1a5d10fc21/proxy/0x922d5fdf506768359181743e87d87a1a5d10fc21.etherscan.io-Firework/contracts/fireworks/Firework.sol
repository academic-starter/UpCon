// SPDX-License-Identifier: MIT

pragma solidity 0.8.2;

import "../ERC721ProjectProxy.sol";

// @title: YourDaytimeFireworks

////////////////////////////////////////////////////////////////////////////
//                                                                        //
//        ░░                                                              //
//         ░░                   ░                                         //
//    ░    ▒▒                 ▒▓▒      ░                                  //
//          ▓▓▒              ▐▒▓▒░     ░░                                 //
//    ▒░   ▒▀█▀             ▐▓▓▓▓▒      ▀▒░           ░░                  //
//    ▓▒  ▐▄▄▌▄▒  ░       ▒██▓███▒░  ▐▓██▌░          ▐▒                   //
//    ░    ▀██▓▒░           ▓▌▄▄▒     ███▓▄░         ▐▌▒             ░    //
//    ▓▀     ▓██▒  ░       ▐███▌▒     ▀███▀ ▒▌░      ▒▓▒            ▐▒    //
//    ▓▓▌▒   ▓██▓▒  ░       ███▓▄    ▀▓▓▓▓░▄▓▌▄  ▐▓▓▓▒░      ░      ▒▒    //
//     ▓█▓░  ▓██▀  ░       ▐▓████▒   ▓██▓▒ ▐▓▓▓▌▒▐▓███▒░  ▒▄▒░      ▒     //
//    ▓██▒    ▓█▒░           ▓███▌▄ ▐███▓█▒▓████▓▄▌▓▓█▒ ▐▓▓██▓▒░ ░▀▒      //
//    ▓▓██▒▓▓████▌░▐▒░       ▐████▓▓▓███▌▀▐██▓▓█████▄▄░░  █████▒░▀▒░      //
//     ▐████▌▓▒▒▓▀░▌▄▄▀▒▒   ▄▄██████████   ▓▓▓▓██████▓▀░▐▄███▓▒██▌▒       //
//      ▓█████████▌▌▓▌▒▒░ ▐▓█████▓█████▓░▄▓▓██▌▓█▓▓▀▀   ███▓▌░███▒        //
//      ▀▓███▌▐████▓███▌▒ ▓█████▒ ▐███▄ ▀▓██████▓▓█▓▒  ▒▀██▀▌▒▓▓▌         //
//      ▐▀▒▓▓░ ▓███▓▌▌█▓▒░  ▓███▓▄░▓██▓▀ ▄▄▓▓▓██▓▓▓▌▒ ░█▀▄▄░░▀██▌▒░       //
//      ▄▒▒▒▒▒ ▓████▀██▓▒░  ▐████▀█████▓▓██▓██▌▓▓██▓▓▒▒█▀▀▓▌░ ▓██▀░░      //
//      ▓███████████▒███▓▒ ▓█████▄▓▓███▀ ▀▒▓██████▓▒▒▓█▓▓█▌▒  ▀██▌░       //
//       ▀▌▀▓██▀████▓▓█▓▓▒ ▀████▓▓██████▒▓█████████▓▒ ███▀░   ░▒▒▒░       //
//       ▀▓▓███▀████▓▒██▀▒▒░████████████▐▀█▓▓▓▓████▌▐▓██▓▒░ ▐▓█▓▓▒        //
//        ▀██▓▌▓█████▌█▓▌▒▀ ▐███████████▄▄████▓▓██▓▒████▓▓▓▌█▌▒█▒         //
//         ▓██▓█▌▀███████▌▒░ ▐██████████▒▀████▌▀██▓▌▄▀███▓▓████▌▒         //
//         ▓▓▓██░ ████▓██▓▌▒ ▓███████████  ▓██▓█████▀▒▌▓▌▒▀███▀░          //
//        ▐█████  ▐████▓███▒░▓█████▓▄████▒▓██▓█████▌▒▒▌▓█▒███▓▀░          //
//         ▐████▒   ▐█████▓░ ▐██████████▓▓▓███▌▒▀██▓▓█▓▓▒▓▓▓█▓▒           //
//         ▐▓▓▓▓▓▒  ▄██████▒ ░▀█████████▀▓█▓▓██▓▓▌▀████▓█▌▒█▓▒            //
//         ░▓███▌░ ███▓▓███▒  ▐█████████ ▓███▓▓███▓█▓▌▒▐██▒▒░             //
//          ██▓▓██████████▓    ███▓▓███▓█████▓▓██████▓▒████▌              //
//          ▓████████████▓▌     ▓█████████████▓█████▓▓▓██▓▒░              //
//           ▐█████████▓▓▓▓░    ████████████████▌████▓██▓▒                //
//           ▐▓▓█████████▓█▒    █████▓█▓ ▀██▓▒▓█▓▒████▓█▓░                //
//            ▐▀ ███████▓█▓▒  ▄  ▀██████▌▄█▓▓▓▒▓▓▒▐▓▓▒▀▓▒░                //
//              ▐▓▓███████▓▒▓▌▒█▓██████▒▓█████▓▒▒▓▀▀█▌▒░▒                 //
//               ▀▓███████▓▓██▒▓███████▓▓█████▓▌██▓▓▒▒▓▒                  //
//                 █████████▓▓▌▐███████████▓██▓▓▀█▓█▓▒░░                  //
//                 ▀▓██████▓▓▌ ░██████████▓▌▓▀░░▐▓█▒▀▀▒▒                  //
//                  ▓██████▓▓▌▒ ▐█████▓███▓▀▌▒░▀█▓▀░▒░                    //
//                  ▀▓█████▓▌▓▓▓▓██████▓▓██▓▓▒▌▄▄█▓▒▒                     //
//                   ▓███████▌▄████████▓▓████▓▓▓██▓▒░                     //
//                   ▀█████▓█▓▓▒████▓█████▓▓▓▓▒▐██▓▓▒                     //
//                   ▓█████▀██▓▒▓██████▀▓▓▓▓▓▌▒▒▓▓▒▀▒                     //
//                   ░▓████████▌▓█████▌ ▐▓▓█▓▓▒▀▓▓▒░                      //
//                    ▐▓███████▌▓▓▓███░  ▒▓▓▓▌▀▒▓▓▒░                      //
//                       ▀▀██▓▓██▓▓███▓▒  ▓▓▌▀▒▒▓▓▒                       //
//                       ▒▓█▓▓▌██▀▓███▌  ▐▌▀▒▒▀▀▓▌░                       //
//                       ▒▓█▓▓▓▀  ▓███▌ ▐▓▌▒▒░▀▓▌░                        //
//                       ▀▌▓█▓▓▒ ▐██████▐▓▀▒▒ ▓▓▌░                        //
//                        ▐▓███▒ ▐▓████▓▒▓▌▒▒▐▓▀▒░                        //
//                         ▐▀▀▒ ░▄▓▓▓▓▓ ▐▓▓▒░                             //
//                           ▒▒▓▌▀▀▀███▄▄▄▀░░░░                           //
//                          ░▒▓▓▌  ░▓███▓▌░ ▒░                            //
//                            ▒▒▒▒▄▓▓███▓▒░░ ░                            //
//                              ▒▀▓█████▓▒░                               //
//                              ░▒▒▀▓███▓▒░                               //
//                                ░░▐▓█▓▓▒                                //
//                                  ▐▒▒▒▒░                                //
//                                  ░▒▒▌▀░                                //
//                                   ▐▌▒░                                 //
//                                   ░▀▀▒                                 //
//                                    ░░                                  //
//                                                                        //
////////////////////////////////////////////////////////////////////////////

contract Firework is ERC721ProjectProxy {
    constructor(address _impl) ERC721ProjectProxy(_impl, "YourDaytimeFireworks", "YDF") {}
}