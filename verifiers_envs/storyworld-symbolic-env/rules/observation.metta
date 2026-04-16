(= (propagate-observation (steal-event $thief $victim $object))
   (do
     (add-atom &self (visible-fact Alice (saw (steal-event $thief $victim $object))))
     (add-atom &self (visible-fact Guard1 (saw (steal-event $thief $victim $object))))
     (add-atom &self (visible-fact Guard1 (knows-thief $thief)))
     (add-atom &self (arrest-ready Guard1 $thief))
     (add-atom &self (trust-delta Guard1 $thief -0.60 witnessed))))

(= (propagate-observation (buy-event $buyer $seller $object $payment))
   (do
     (add-atom &self (visible-fact Guard1 (saw (buy-event $buyer $seller $object $payment))))))
