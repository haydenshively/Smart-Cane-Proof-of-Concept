//
//  ViewController.swift
//  Sixth Sense
//
//  Created by Hayden Shively on 3/7/20.
//  Copyright © 2020 Golden Age Technologies LLC. All rights reserved.
//

import UIKit
import IKEventSource

class ViewController: UIViewController {
    
    let impact = UIImpactFeedbackGenerator(style: .rigid)
    var eventSource: EventSource?

    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        
        let serverURL = URL(string: "http://172.20.10.6:5000/updates.cam")!
        eventSource = EventSource(url: serverURL)
        
        eventSource?.onComplete { statusCode, reconnect, error in
            DispatchQueue.main.asyncAfter(deadline: .now() + .milliseconds(100)) {
                self.eventSource?.connect()
            }
        }
        
        eventSource?.onMessage { id, event, data in
            if data == nil {return}
            var noParenths = data!.replacingOccurrences(of: "(", with: "")
            noParenths = noParenths.replacingOccurrences(of: ")", with: "")
            let noSpaces = noParenths.replacingOccurrences(of: " ", with: "")
            let split = noSpaces.split(separator: ",")
            
            guard let size = Float(split[0]),
                let x = Int(split[1]),
                let y = Int(split[2]) else {
                    return
            }
//            print((size, x, y))
            if abs(x - 600) > 100 {
//                print("X varied too much")
                self.impact.impactOccurred()
            }
        }
        
        eventSource?.connect()
    }


}
