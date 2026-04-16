(= (step-world $actor $action)
   (do
     (apply-action $action)
     (project-step-visibility $action)
     (score-world)))

(= (project-step-visibility (steal $thief $victim $object))
   (propagate-observation (steal-event $thief $victim $object)))

(= (project-step-visibility (buy $buyer $seller $object $payment))
   (propagate-observation (buy-event $buyer $seller $object $payment)))

(= (project-step-visibility $action)
   noop)
